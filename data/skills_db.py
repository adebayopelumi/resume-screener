SKILLS = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql", "bash", "shell",
        "php", "html", "css", "dart", "flutter"
    ],
    "ml_ai": [
        "machine learning", "deep learning", "neural networks", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "transformers", "llm", "gpt", "bert", "pytorch", "tensorflow", "keras",
        "scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
        "hugging face", "langchain", "openai", "stable diffusion", "rag",
        "retrieval augmented generation", "fine-tuning", "transfer learning",
        "object detection", "image segmentation", "yolo", "resnet", "vgg",
        "attention mechanism", "embedding", "vector database", "pinecone", "faiss",
        "mlflow", "weights & biases", "wandb"
    ],
    "data": [
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "tableau", "power bi",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "data analysis", "data science", "data engineering", "etl",
        "apache spark", "pyspark", "hadoop", "airflow", "dbt",
        "data visualization", "statistics", "a/b testing", "feature engineering"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "ci/cd", "github actions", "jenkins", "terraform", "ansible",
        "linux", "git", "github", "gitlab", "bitbucket", "microservices",
        "rest api", "graphql", "fastapi", "flask", "django", "node.js",
        "serverless", "lambda", "ec2", "s3", "sagemaker"
    ],
    "soft_skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "project management", "agile", "scrum",
        "collaboration", "time management", "mentoring", "research"
    ]
}

ALL_SKILLS = []
for category_skills in SKILLS.values():
    ALL_SKILLS.extend(category_skills)

CATEGORY_LABELS = {skill: cat for cat, skills in SKILLS.items() for skill in skills}
