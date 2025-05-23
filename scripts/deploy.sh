conda activate cedschedulerapp && \
cd /root/project/CedSchedulerApp/cedschedulerapp/master && \
python app.py --host 0.0.0.0 --port 12002 --training-host 10.31.12.20  --training-port 5000


conda activate cedschedulerapp && \
cd /root/project/CedSchedulerApp/cedschedulerapp/worker && \
python app.py --master-host 10.31.12.19 --master-port 12002 --region 1 --type 训练 --id training-node-1 

