apt-get update -y
apt-get install wget -y

wget https://archive.apache.org/dist/sqoop/1.99.7/sqoop-1.99.7-bin-hadoop200.tar.gz
tar -xvf sqoop-1.99.7-bin-hadoop200.tar.gz
mv sqoop-1.99.7-bin-hadoop200 /usr/lib/sqoop
export SQOOP_HOME=/usr/lib/sqoop export PATH=$PATH:$SQOOP_HOME/bin
source ~/.bashrc

tail -f /dev/null