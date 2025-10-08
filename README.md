# Document Review Analytics Dashboard

This dashboard visualizes and animates InSource’s document review operations from 2020 to 2025.

It shows:
- Monthly review hours
- Documents processed
- Affirmative vs. Defensive trends
- Case-level and jurisdictional work
- Billable percentage

Built using Python, Dash, Plotly, and Pandas.

---

## 📁 Files Included

- `app.py` – The interactive dashboard app
- `combined_document_review.csv` – Cleaned data
- `requirements.txt` – Package list
- `render.yaml` – For free deployment on [Render](https://render.com)

---

## 💻 How to Run Locally

```bash
git clone https://github.com/fahmpr/document-review-analytics.git
cd document-review-analytics
pip install -r requirements.txt
python app.py
