# FiscoCaliperSc
一次基于Fisco-Bcos的caliper压测记录总结的自动化脚本  
  
脚本测试环境：  
Ubuntu 20.04.3 LTS  
FISCO-BCOS 2.7.2  
Docker version 20.10.11  
docker-compose version 1.24.0  

使用：  
1.准备合约，放在caliper-bechmarks目录下  
2.准备工作负载模块，放在caliper-benchmarks目录下  
3.启动 ```python3 proControll.py hp  