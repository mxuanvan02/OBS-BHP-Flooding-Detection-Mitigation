# 🌐 Burst Header Packet Flooding Detection using Random Forest

<p align="center">
  <img src="Images/Project Snapshot.png" width="50%" alt="Project Snapshot">
</p>

## 📌 Overview

This project applies **Machine Learning** to detect **Burst Header Packet (BHP) Flooding attacks** in Optical Burst Switching (OBS) networks. The objective is to accurately classify network nodes as legitimate or malicious while minimizing computational overhead for real-time deployment.

Using a publicly available cybersecurity dataset, a **Random Forest classifier** combined with **Wrapper Feature Selection** was developed to identify the most informative network traffic features for intrusion detection.

---

## 🎯 Business Problem

Optical Burst Switching (OBS) networks improve high-speed data transmission but remain vulnerable to **Burst Header Packet (BHP) Flooding attacks**, a form of Denial-of-Service (DoS) attack.

These attacks can:

- 🚫 Reserve network bandwidth without transmitting actual data
- 📉 Reduce network performance
- ⚠️ Deny legitimate users access to network resources
- 💸 Increase infrastructure and operational costs

The goal of this project was to develop an efficient machine learning model capable of detecting malicious nodes while using as few network features as possible.

---

## 💡 Key Insights

- 🎯 **The Random Forest model achieved 100% classification accuracy on the dataset.**
- ⚡ **Only three network features were required to maintain perfect performance after Wrapper Feature Selection.**
- 📉 **Reducing the feature set significantly lowers computational cost without sacrificing predictive accuracy.**
- 🛡️ **The proposed approach is suitable for real-time intrusion detection where low latency and resource efficiency are essential.**
- 🌐 **Feature selection proved as valuable as model selection by simplifying deployment while preserving performance.**

---

## 📷 Results

### Feature Importance (Information Gain)

<img src="Images/Feature Information Gain.png" width="70%" alt="Feature Information Gain">

### Wrapper Feature Selection Results

<img src="Images/Wrapper Feature Selection Results.png" width="70%" alt="Wrapper Feature Selection Results">

### Confusion Matrix

<img src="Images/Confusion Matrix.png" width="70%" alt="Confusion Matrix">
---

## 📊 Dataset

This project uses the **Burst Header Packet (BHP) Flooding Attack on Optical Burst Switching (OBS) Network Dataset** from the **UCI Machine Learning Repository**.

**Dataset Summary**

- 📄 1,075 network instances
- 📈 21 predictor features
- 🎯 4 target classes
- 🌐 Publicly available dataset

**Target Classes**

- NB-No Block
- No Block
- NB-Wait
- Block

---

## 🧹 Data Preparation

The dataset was prepared using several preprocessing techniques:

- Missing value removal
- Feature normalization
- Wrapper Feature Selection (Sequential Backward Selection)
- Information Gain feature ranking

The objective was to identify the smallest subset of features capable of maintaining high classification performance.

---

## 🤖 Modeling Approach

### 🌲 Random Forest Classifier

A Random Forest model was trained to classify network nodes into four behavioral categories.

**Configuration**

- 10 Decision Trees
- Minimum split size = 5
- Stratified 10-Fold Cross Validation

---

## 📏 Model Evaluation

### Validation Strategy

- ✅ Stratified 10-Fold Cross Validation

### Evaluation Metrics

- Accuracy
- Precision
- Sensitivity (Recall)
- Specificity
- Confusion Matrix

---

## 🛠️ Tools & Technologies

- 📊 Microsoft Excel
- 🍊 Orange Data Mining

---

## 🚀 Skills Demonstrated

- Machine Learning Classification
- Random Forest
- Feature Selection
- Wrapper Methods
- Information Gain
- Data Preprocessing
- Cross Validation
- Model Evaluation
- Confusion Matrix Analysis
- Cybersecurity Analytics
- Network Traffic Classification


---

## 🔮 Future Improvements

Potential enhancements include:

- Compare Random Forest with XGBoost and LightGBM
- Evaluate deep learning approaches for intrusion detection
- Test on additional network security datasets
- Optimize hyperparameters for deployment
- Develop a real-time intrusion detection pipeline

---

## 📚 Dataset Source

The dataset used in this project is publicly available through the **UCI Machine Learning Repository** and contains simulated Optical Burst Switching network traffic for Burst Header Packet Flooding attack detection.
