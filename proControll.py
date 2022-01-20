import sys,os

"""
注意，此脚本只能帮助运行成功，或者了解caliper模式准备动手写脚本的人
因为本脚本的初衷是偷懒而不是从0开始协助搭建
所以脚本本身还有很多不完善的地方

不要盲目相信这个垃圾脚本
还有很多地址需要修改哦~
"""

fileName = r'./docker-compose.yaml'

#--------------------------------confi.yaml--------------------------------#
configYamldata = """
---
test:
  name: dsfasfasdfsdfa
  description: This is a helloworld benchmark of FISCO BCOS for caliper
  clients:
    type: local
    number: 1
  rounds:
  - label: set
    description: Test performance of setting name
    txNumber:
    - {}
    rateControl:
    - type: fixed-rate
      opts:
        tps: 1300
    callback: SC0-set.js
monitor:
  type:
  - docker
  docker:
    name:
{}
  process:
    - command: node
      multiOutput: avg
  interval: 0.5
"""

#--------------------------------config.ini--------------------------------#
configData = """
[rpc]
    channel_listen_ip=0.0.0.0
    channel_listen_port={}
    jsonrpc_listen_ip=0.0.0.0
    jsonrpc_listen_port={}
[p2p]
    listen_ip=0.0.0.0
    listen_port={}
    ; nodes to connect  
{}

[certificate_blacklist]
    ; crl.0 should be nodeid, nodeid's length is 128
    ;crl.0=

[certificate_whitelist]
    ; cal.0 should be nodeid, nodeid's length is 128
    ;cal.0=

[group]
    group_data_path=data/
    group_config_path=conf/

[network_security]
    ; directory the certificates located in
    data_path=conf/
    ; the node private key file
    key=node.key
    ; the node certificate file
    cert=node.crt
    ; the ca certificate file
    ca_cert=ca.crt

[storage_security]
    enable=false
    key_manager_ip=
    key_manager_port=
    cipher_data_key=

[chain]
    id=1
    ; use SM crypto or not, should nerver be changed
    sm_crypto=false
    sm_crypto_channel=false

[compatibility]
    ; supported_version should nerver be changed
    supported_version=2.7.2

[log]
    enable=true
    log_path=./log
    ; enable/disable the statistics function
    enable_statistic=false
    ; network statistics interval, unit is second, default is 60s
    stat_flush_interval=60
    ; info debug trace
    level=info
    ; MB
    max_log_file_size=200
    flush=true

[flow_control]
    ; restrict QPS of the node
    ;limit_req=1000
    ; restrict the outgoing bandwidth of the node
    ; Mb, can be a decimal
    ; when the outgoing bandwidth exceeds the limit, the block synchronization operation will not proceed
    ;outgoing_bandwidth_limit=2

"""

#--------------------------------docker-compose.yaml--------------------------------#
defaultData = """
version: "3"

services:
"""
addData = """
  node{}:
    image: fiscoorg/fiscobcos:latest
    ports:
      - "{}:{}"
      - "{}:{}"
      - "{}:{}"
    working_dir: /data
    volumes:
      - /root/benchmarks/xiaoyuetest/nodes/127.0.0.1/node{}/:/data
    deploy:
      resources:
          limits:
              cpus: '{}'
              memory: {}M
          reservations:
              # cpus: '{}'
              memory: {}M
    container_name: node{}
    command: /usr/local/bin/fisco-bcos -c config.ini
    {}
"""

def usage():
    usagetext = '\nUsage:\nparams: nodeNum limCpu limMemo reCpu limMemo txNumber\n' \
                '\t1. nodenum :\t必填,需要进行压测的节点数量，上限100\n' \
                '\t2. limcpu  :\t可选,容器CPU的极限值，不填默认为0.1\n' \
                '\t3. limmemo :\t可选,容器内存极限值，不填默认为1024m \n' \
                '\t4. recpu   :\t可选,容器CPU常规值，不填默认为0.1)\n' \
                '\t5. limmemo :\t可选,容器内存常规值，不填默认为200m)\n' \
                '\t6. txNumber:\t可选,压测数量，不填默认为1000)\n\n'

    usagetext = usagetext + "\teg: default allocation, 5node , use cmdline:\n\n"
    usagetext = usagetext + "\tpython3 proControll.py 5\n\n"

    usagetext = usagetext + "\teg: default allocation, 5node limcpu0.3 limmemo 251 ... , use cmdline:\n\n"
    usagetext = usagetext + "\tpython3 proControll.py 3 0.3 251 0.1 201 1000\n"
    
    usagetext = usagetext + "\t     「如需添加配置参数，则4个选填参数均需填」\n"

    print(usagetext)


def fixConfigyaml(nodeNum,txNumber,configYamldata):
  insertData = ""
  for i in range(int(nodeNum)):
    insertData+="      - node{}".format(i)+"\n"
  configYamldata = configYamldata.format(txNumber,insertData)
  with open("./config.yaml","w") as w:
    w.write(configYamldata)


def main(argv):
    """主函数"""

    os.system("rm -rf ./nodes")

    if argv[0] == "help" or argv[0]== "hp":
        usage()
        exit()

    elif len(argv) == 1:
        nodeNum = argv[0]
        limitsCpu = 0.1
        limitsMemory = 240
        resCpu = 0.1
        resMemory = 200
        txNumber = 1000
    else:
        nodeNum = argv[0]
        limitsCpu = float(argv[1])
        limitsMemory = int(argv[2])
        resCpu = float(argv[3])
        resMemory = int(argv[4])
        try:
          txNumber = int(argv[5])
        except Exception:
          txNumber = 1000

    os.system("bash build_chain.sh -l 127.0.0.1:{} -p 30700,20700,7545".format(nodeNum))

    channelPor = 20700
    rpcPort = 7545
    p2pPort = 30700

    fixConfigyaml(nodeNum,txNumber,configYamldata)
    
    _recoverDefault(nodeNum)

    for i in range(int(nodeNum)):
        _insertOne(i,channelPor,rpcPort,p2pPort,i,limitsCpu,limitsMemory,resCpu,resMemory,i)
        channelPor+=1
        rpcPort+=1
        p2pPort+=1

    fixConfig(nodeNum)

    os.system("npx caliper benchmark run --caliper-workspace caliper-benchmarks --caliper-benchconfig /root/benchmarks/xiaoyuetest/config.yaml  --caliper-networkconfig /root/benchmarks/xiaoyuetest/fisco.json")

    _recoverDefault(nodeNum)

def _recoverDefault(nodeNum):
    with open(fileName, 'w') as f:
        f.write(defaultData)
    for i in range(int(nodeNum)):
        with open("./nodes/127.0.0.1/node{}/config.ini".format(i),"w") as f:
            f.write("https://x1a0.net")

def _insertOne(nodeId1,channelPor,
                                rpcPort,
                                p2pPort,
                                nodeId2,
                                limitsCpu,
                                limitsMemory,
                                resCpu,
                                resMemory,
                                nodeId3):
    fixdata = """depends_on:
      - "node{}"
    """

    if nodeId1>0:
      wrData = addData.format(nodeId1,channelPor,
                                          channelPor,
                                          rpcPort,
                                          rpcPort,
                                          p2pPort,
                                          p2pPort,
                                          nodeId2,
                                          limitsCpu,
                                          limitsMemory,
                                          resCpu,
                                          resMemory,
                                          nodeId3,
                                          fixdata.format(int(nodeId3)-1))
    if nodeId1 == 0:
        wrData = addData.format(nodeId1,channelPor,
                                          channelPor,
                                          rpcPort,
                                          rpcPort,
                                          p2pPort,
                                          p2pPort,
                                          nodeId2,
                                          limitsCpu,
                                          limitsMemory,
                                          resCpu,
                                          resMemory,
                                          nodeId3,
                                          "")
    with open(fileName, 'a+') as f:
        f.write(wrData)



def fixConfig(nodeNum):
    """config.ini配置文件修改函数"""
    baseline = "    node.{}=172.17.0.1:{}"
    basedata = ""

    for i in range(int(nodeNum)):
        basedata+=baseline.format(i,30700+i)+"\n"

    for i in range(int(nodeNum)):
        insertconfig = configData.format(20700+i,7545+i,30700+i,basedata)
        with open("./nodes/127.0.0.1/node{}/config.ini".format(i),"w") as f:
            f.write(insertconfig)


if __name__ == "__main__":
    main(sys.argv[1:])
