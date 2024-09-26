git clone https://github.com/chupino/flaskvoting.git flask
cd flask

docker build -t flaskvoting .

if [ $? -eq 0 ]; then
    echo "bien"
else
    echo "mal"
    exit 1
fi

docker run -dp 8000:80 --name=flask-app flaskvoting