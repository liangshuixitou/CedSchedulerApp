conda activate cedschedulerapp && \
cd ~/project/CedSchedulerApp/cedschedulerapp/master && \
python app.py --host 0.0.0.0 --port 12002 --training-host 10.31.12.20  --training-port 5000 --inference-host 10.212.70.38  --inference-port 37000


conda activate cedschedulerapp && \
cd /root/project/CedSchedulerApp/cedschedulerapp/worker && \
python app.py --master-host 10.31.12.19 --master-port 12002 --region 1 --type 训练 --id training-node-1 

conda activate cedschedulerapp && \
cd /root/project/CedSchedulerApp/cedschedulerapp/worker && \
python app.py --master-host 10.31.12.19 --master-port 12002 --region 2 --type 训练 --id training-node-2 

conda activate cedschedulerapp && \
cd /root/project/CedSchedulerApp/cedschedulerapp/worker && \
python app.py --master-host 10.31.12.19 --master-port 12002 --region 3 --type 训练 --id training-node-3