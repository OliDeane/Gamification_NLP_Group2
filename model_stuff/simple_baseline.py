import argparse
import json
import os
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score


def read_jsonl_lines(input_file: str) -> List[dict]:
    # Parse the input file from JSONL to a list of dictionaries.
    with open(input_file) as f:
        lines = f.readlines()
        return [json.loads(l.strip()) for l in lines]


def get_embedding(embs_model, text):
    # use sentence-transformers to get sentence embedding
    return embs_model.encode([text])


def get_embeddings(embs_model, train_records):
    # embedding_dimensions = 768
    embedding_dimensions = 1024
    N = len(train_records)

    class_labels = np.array(["A", "B", "C"])

    cq_embs = np.empty((N, embedding_dimensions))
    A_embs = np.empty((N, embedding_dimensions))
    B_embs = np.empty((N, embedding_dimensions))
    C_embs = np.empty((N, embedding_dimensions))
    train_labels = np.empty((N))

    print("loading embeddings for %i records" % N)

    for i, record in enumerate(train_records):
        cq_embs[i] = get_embedding(
            embs_model, record["context"] + " " + record["question"]
        )
        A_embs[i] = get_embedding(embs_model, record["answerA"])
        B_embs[i] = get_embedding(embs_model, record["answerB"])
        C_embs[i] = get_embedding(embs_model, record["answerC"])
        train_labels[i] = np.argwhere(class_labels == record["correct"])[0][0] + 1

        if np.mod(i, 100) == 0:
            print(i)

    return cq_embs, A_embs, B_embs, C_embs, train_labels


def main(train_file, input_file, output_file):
    # load an embeddings model
    embs_model = SentenceTransformer(
        "roberta-large-nli-stsb-mean-tokens"
    )  # 'distilbert-base-nli-mean-tokens')

    # Read the records from the training set.
    train_records = read_jsonl_lines(train_file)
    # train_records = train_records[:100]

    if os.path.exists("traincqembs.txt"):
        cq_embs = np.genfromtxt("traincqembs.txt")
        A_embs = np.genfromtxt("trainA_embs.txt")
        B_embs = np.genfromtxt("trainB_embs.txt")
        C_embs = np.genfromtxt("trainC_embs.txt")
        train_labels = np.genfromtxt("trainlabels.txt")
    else:
        cq_embs, A_embs, B_embs, C_embs, train_labels = get_embeddings(
            embs_model, train_records
        )

        np.savetxt("traincqembs.txt", cq_embs)
        np.savetxt("trainA_embs.txt", A_embs)
        np.savetxt("trainB_embs.txt", B_embs)
        np.savetxt("trainC_embs.txt", C_embs)
        np.savetxt("trainlabels.txt", train_labels)

    # multiply the embeddings to compute interactions between context+question and answer
    joint_embs_A = cq_embs * A_embs
    joint_embs_B = cq_embs * B_embs
    joint_embs_C = cq_embs * C_embs
    joint_embs = np.concatenate((joint_embs_A, joint_embs_B, joint_embs_C), axis=0)

    # get binary training labels for each triple
    joint_labels = np.concatenate(
        (
            (train_labels == 1).astype(int),
            (train_labels == 2).astype(int),
            (train_labels == 3).astype(int),
        ),
        axis=0,
    )

    print("Completed loading data and embeddings.")

    # train a classifier
    classifier = RandomForestRegressor(n_estimators=1000, n_jobs=-1).fit(
        joint_embs, joint_labels
    )

    print("Completed training.")

    # Read the records from the test set.
    test_records = read_jsonl_lines(input_file)
    # test_records = test_records[:500]
    Ntest = len(test_records)

    if os.path.exists("testcqembs.txt"):
        cq_embs = np.genfromtxt("testcqembs.txt")
        A_embs = np.genfromtxt("testA_embs.txt")
        B_embs = np.genfromtxt("testB_embs.txt")
        C_embs = np.genfromtxt("testC_embs.txt")
        test_labels = np.genfromtxt("testlabels.txt")
    else:
        cq_embs, A_embs, B_embs, C_embs, test_labels = get_embeddings(
            embs_model, test_records
        )

        np.savetxt("testcqembs.txt", cq_embs)
        np.savetxt("testA_embs.txt", A_embs)
        np.savetxt("testB_embs.txt", B_embs)
        np.savetxt("testC_embs.txt", C_embs)
        np.savetxt("testlabels.txt", test_labels)

    # Make predictions for each example in the test set.
    predicted_answers = np.empty(Ntest)
    for i in range(Ntest):
        pred_A = classifier.predict_proba(cq_embs[i : i + 1] * A_embs[i : i + 1])[0][1]
        pred_B = classifier.predict_proba(cq_embs[i : i + 1] * B_embs[i : i + 1])[0][1]
        pred_C = classifier.predict_proba(cq_embs[i : i + 1] * C_embs[i : i + 1])[0][1]

        # normalise
        preds = np.array([pred_A, pred_B, pred_C]) / (pred_A + pred_B + pred_C)

        predicted_answers[i] = np.argmax(preds) + 1

    print("Test set accuracy: %f" % accuracy_score(test_labels, predicted_answers))

    # Write the predictions to the output file.
    with open(output_file, "w") as f:
        for p in predicted_answers:
            f.write(str(p))
            f.write("\n")
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A simple baseline that uses multi-class classifier on top of pretrained embeddings."
    )
    parser.add_argument(
        "--train-file",
        type=str,
        required=True,
        help="Location of training records",
        default=None,
    )
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Location of test records",
        default=None,
    )
    parser.add_argument(
        "--output-file",
        type=str,
        required=True,
        help="Location of predictions",
        default=None,
    )

    args = parser.parse_args()
    print("====Input Arguments====")
    print(json.dumps(vars(args), indent=2, sort_keys=True))
    print("=======================")
    main(args.train_file, args.input_file, args.output_file)
