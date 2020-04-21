# Software-Defined System - Rock Paper Scissor
## How to set up Kubernetes cluster
1. Two Master Nodes, and One Loadbalancer Spec:
    - Ubuntu 16.04 VM
    - 2 CPU Cores
    - Ram: 4 GB
2. Four Worker Nodes Spec:
    - Raspberry pi 3 B+ with operating system Raspbain Strench Lite
    - Create empty file “ssh” and store in Raspberry pi
3. Set Static IP Address in 2 Master Nodes, 4 Worker Nodes and Loadbalancer
    - Worker Node
        1. `192.168.0.111`
        2. `192.168.0.112`
        3. `192.168.0.114`
        4. `192.168.0.124`
    - Master Node
        1. `192.168.0.123`
        2. `192.168.0.234`
    - Loadbalancer
        1. `192.168.0.222`
4. Connect computer1 which have Master Node and Lordbalancer and computer2 which have only Master Node with TP-Link router though wireless connection and connect raspberry pi with TP-Link router though Ethernet cable
5. Worker node configuration
    - Install docker and set its permission
        ```
        $ curl -sSL get.docker.com | sh && \
        $ sudo usermod pi -aG docker && \
        $ newgrp dockerDisble swap
        ```
    - Disable swap
        ```
        $ sudo dphys-swapfile swapoff && \
        $ sudo dphys-swapfile uninstall && \
        $ sudo update-rc.d dphys-swapfile remove
        ```
    - Edit the `/boot/cmdline.txt` file. Add the following in the end of the file
        ```
        $ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory
        ```
    - Reboot
        ```
        $ sudo reboot
        ```
    - Edit the `/etc/apt/sources.list.d/kubernetes.list` by add following in the file
        ```
        deb http://apt.kubernetes.io/ kubernetes-xenial main
        ```
    - Add the key
        ```
        $ curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
        ```
    - Update with new repo
        ```
        $ sudo apt-get update
        ```
    - Install `kubeadm`
        ```
        $ sudo apt-get install –qy kubeadm
        ```
6. Master node and load-balancer configuration
    - Installing `cfssl` on load-balancer
        1. Download the binaries
            ```
            $ wget https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
            $ wget https://pkg/cfssl.org/R1.2/cfssljson_linx-amd64
            ```
        2. Add the execution permission to the binaries
            ```
            $ chmod +x cfssl*
            ```
        3. Move the binaries to `/usr/local/bin`.
            ```
            $ sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
            $ sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
            ```
    - Installing kubectl on loadbalancer
        1. Download the binary
            ```
            $ wget https://storage.googleapis.com/kubernetes-release/release/v1.12.1/bin/linux/amd64/kubectl
            ```
        2. Add the execution permission to the binary
            ```
            $ chmod +x kubectl
            ```
        3. Move the binary to `/usr/local/bin`
            ```
            $ sudo mv kubectl /usr/local/bin
            ```
    - Installing the HAProxy load balancer
        1. Update the machine
            ```
            $ sudo apt-get update
            $ sudo apt-get upgrade
            ```
        2. Install HAProxy
            ```
            $ sudo apt-get install haproxy
            ```
        3. Configure HAProxy to load-balance the traffic between the two Kubernetes master nodes
            ```
            $ sudo nano /etc/haproxy/haproxy.cfg
            global
            …
            Default
            …
            frontend kubernetes
            bind 192.168.0.222:6443
            option tcplog
            mode tcp
            default_backend kubernetes-master-nodes

            backend kubernetes-master-nodes
            mode tcp
            balance roundrobin
            option tcp-check
            server k8s-master-0 192.168.0.123 check fall 2 rise 1
            server k8s-master-1 192.168.0.234 check fall 2 rise 1
            ```
        4. Restart HAProxy
            ```
            $ sudo systemctl restart haproxy
            ```
        5. Creating A certificate authority
            - Create the certificate authority configuration file
                ```
                $ nano ca-config.json
                {
                    “signing”: {
                        “default”: {
                            “expiry”: “8760h”
                        },
                        “profiles”: {
                            “kubernetes”: {
                                “usages”: [“signing”, “key encipherment”, “server auth”, “client auth”],
                                “expiry”: “8760h”
                            }
                        }
                    }
                }
                ```
            - Create the certificate authority signing request configuration file
                ```
                $ nano ca-csr.json
                {
                    “CN”: “Kubernates”,
                    “key”: {
                        “algo”: “rsa”,
                        “size”: 2048
                    },
                    “names”:[
                        {
                            “C”: “IE”,
                            “L”: “Cork”,
                            “O”: “Kubernetes”,
                            “OU”: “CA”,
                            “ST”: “Cork Co.”
                        }
                    ]
                }
                ```
        6. Generate the certificate authority certificate and private key
            ```
            $ cfssl gencert –initca ca-csr.json | cfssljson –bare ca
            ```
    - Creating the certificate for the Etcd cluster
        1. Create the certificate signing request configuration file
            ```
            $ nano kubernetes-csr.json
            {
                “CN”: “kubernetes”,
                “key”: {
                    “algo”: “rsa”,
                    “size”: 2048
                },
                “names”: [
                    {
                        “C”: “IE”,
                        “L”: “Cork”,
                        “O”: “Kubernetes”,
                        “OU”: “Kubernetes”,
                        “ST”: “Cork Co.”
                    }
                ]
            }
            ```
        2. Generate the certificate and private key
            ```
            $ cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=ca-config.json \
            -hostname=192.168.0.123,192.168.0.234,192.168.0.222,127.0.0.1,kubernetes.default \
            -profile=kubernetes kubernetes-csr.json | \
            cfssljson –bare kubernetes
            ```
        3. Copy the certificate to each nodes
            ```
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.123:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.234:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.222:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.112:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.111:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.124:~
            scp ca.pem kubernetes.pem kubernetes-key.pem {USERNAME}@192.168.0.114:~
            ```
    - Prepare the `192.168.0.123`, `192.168.0.234` machine
        1. Get administrator privileges
            ```
            $ sudo -s
            ```
        2. Add the Docker repository key
            ```
            $ curl –fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
            ```
        3. Add the Docker repository
            ```
            $ add-apt-repository \
            "deb https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
            $(lsb_release -cs) \
            stable"
            ```
        4. Update the list of packages
            ```
            $ apt-get update
            ```
        5. Install `Docker 17.03`
            ```
            $ apt-get install -y docker-ce=$(apt-cache madison docker-ce | grep 17.03 | head -1 | awk '{print $3}')
            ```
        6. Add the Google repository key.
            ```
            $ curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
            ```
        7. Add the Google repository.
            ```
            $ nano /etc/apt/sources.list.d/kubernetes.list
            deb http://apt.kubernetes.io kubernetes-xenial main
            ```
        8. Update the list of packages.
            ```
            $ apt-get update
            ```
        9. Install `kubelet`, `kubeadm` and `kubectl`.
            ```
            $ apt-get install kubelet kubeadm kubectl
            ```
        10. Disable the swap.
            ```
            $ swapoff -a
            $ sed -i '/ swap / s/^/#/' /etc/fstab
            ```
    - Installing and configuring `Etcd` on the `192.168.0.123` machine
        1. Create a configuration directory for Etcd.
            ```
            $ sudo mkdir /etc/etcd /var/lib/etcd
            ```
        2. Move the certificates to the configuration directory.
            ```
            $ sudo mv ~/ca.pem ~/kubernetes.pem ~/kubernetes-key.pem /etc/etcd
            ```
        3. Download the etcd binaries.
            ```
            $ wget https://github.com/coreos/etcd/releases/download/v3.3.9/etcd-v3.3.9-linux-amd64.tar.gz
            ```
        4. Extract the etcd archive.
            ```
            $ tar xvzf etcd-v3.3.9-linux-amd64.tar.gz
            ```
        5. Move the etcd binaries to /usr/local/bin.
            ```
            $ sudo mv etcd-v3.3.9-linux-amd64/etcd* /usr/local/bin/
            ```
        6. Create an etcd systemd unit file.
            ```
            $ sudo vim /etc/systemd/system/etcd.service
            [Unit]
            Description=etcd
            Documentation=https://github.com/coreos


            [Service]
            ExecStart=/usr/local/bin/etcd \
            --name 192.168.0.123 \
            --cert-file=/etc/etcd/kubernetes.pem \
            --key-file=/etc/etcd/kubernetes-key.pem \
            --peer-cert-file=/etc/etcd/kubernetes.pem \
            --peer-key-file=/etc/etcd/kubernetes-key.pem \
            --trusted-ca-file=/etc/etcd/ca.pem \
            --peer-trusted-ca-file=/etc/etcd/ca.pem \
            --peer-client-cert-auth \
            --client-cert-auth \
            --initial-advertise-peer-urls https://192.168.0.123:2380 \
            --listen-peer-urls https://192.168.0.123:2380 \
            --listen-client-urls https://192.168.0.123:2379,http://127.0.0.1:2379 \
            --advertise-client-urls https://192.168.0.123:2379 \
            --initial-cluster-token etcd-cluster-0 \
            --initial-cluster 192.168.0.123=https://192.168.0.123:2380,192.168.0.234=https://192.168.0.234:2380 \
            --initial-cluster-state new \
             --data-dir=/var/lib/etcd
            Restart=on-failure
            RestartSec=5

            [Install]
            WantedBy=multi-user.target
            ```
        7. Reload the daemon configuration.
            ```
            $ sudo systemctl daemon-reload
            ```
        8. Enable etcd to start at boot time.
            ```
            $ sudo systemctl enable etcd
            ```
        9. Start etcd.
            ```
            $ sudo systemctl start etcd
            ```
    - Installing and configuring `Etcd` on the `192.168.0.234` machine
        1. Create a configuration directory for `Etcd`.
            ```
            $ sudo mkdir /etc/etcd /var/lib/etcd
            ```
        2. Move the certificates to the configuration directory.
            ```
            $ sudo mv ~/ca.pem ~/kubernetes.pem ~/kubernetes-key.pem /etc/etcd
            ```
        3. Download the etcd binaries.
            ```
            $ wget https://github.com/coreos/etcd/releases/download/v3.3.9/etcd-v3.3.9-linux-amd64.tar.gz
            ```
        4. Extract the etcd archive.
            ```
            $ tar xvzf etcd-v3.3.9-linux-amd64.tar.gz
            ```
        5. Move the etcd binaries to `/usr/local/bin`.
            ```
            $ sudo mv etcd-v3.3.9-linux-amd64/etcd* /usr/local/bin/
            ```
        6. Create an etcd systemd unit file.
            ```
            $ sudo vim /etc/systemd/system/etcd.service
            [Unit]
            Description=etcd
            Documentation=https://github.com/coreos

            [Service]
            ExecStart=/usr/local/bin/etcd \
            --name 192.168.0.234 \
            --cert-file=/etc/etcd/kubernetes.pem \
            --key-file=/etc/etcd/kubernetes-key.pem \
            --peer-cert-file=/etc/etcd/kubernetes.pem \
            --peer-key-file=/etc/etcd/kubernetes-key.pem \
            --trusted-ca-file=/etc/etcd/ca.pem \
            --peer-trusted-ca-file=/etc/etcd/ca.pem \
            --peer-client-cert-auth \
            --client-cert-auth \
            --initial-advertise-peer-urls https://192.168.0.234:2380 \
            --listen-peer-urls https://192.168.0.234:2380 \
            --listen-client-urls https://192.168.0.234:2379,http://127.0.0.1:2379 \
            --advertise-client-urls https://192.168.0.234:2379 \
            --initial-cluster-token etcd-cluster-0 \
            --initial-cluster 192.168.0.123=https://192.168.0.123:2380,192.168.0.234=https://192.168.0.234:2380\
            --initial-cluster-state new \
            --data-dir=/var/lib/etcd
            Restart=on-failure
            RestartSec=5

            [Install]
            WantedBy=multi-user.target
            ```
        7. Reload the daemon configuration.
            ```
            $ sudo systemctl daemon-reload
            ```
        8. Enable etcd to start at boot time.
            ```
            $ sudo systemctl enable etcd
            ```
        9. Start etcd.
            ```
            $ sudo systemctl start etcd
            ```
        10. Verify that the cluster is up and running.
            ```
            $ ETCDCTL_API=3 etcdctl member list
            ```
    - Initializing the `192.168.0.123` master node
        1. Create the configuration file for `kubeadm`.
            ```
            $ nano config.yaml
            apiVersion: kubeadm.k8s.io/v1beta1
            kind: MasterConfiguration
            tokenTTL: “0”
            ---
            apiVersion: kubeadm.k8s.io/v1beta1
            kind: ClusterConfiguration
            kubernetesVersion: stable
            apiServer:
                certSANs:
                    - 192.168.0.222
            controlPlaneEndpoint: "192.168.0.222:6443"
            etcd:
                external:
                    endpoints:
                        - https://192.168.0.123:2379
                        - https://192.168.0.234:2379
                    caFile: /etc/etcd/ca.pem
                    certFile: /etc/etcd/kubernetes.pem
                    keyFile: /etc/etcd/kubernetes-key.pem
            ```
        2. Initialize the machine as a master node.
            ```
            $ sudo kubeadm init --config=config.yaml
            ```
        3. Copy the certificates to the other masters.
            ```
            $ sudo scp -r /etc/kubernetes/pki sguyennet@192.168.0.234:~
            ```
        ◦ Setup `kubeconfig`
            ```
            mkdir -p $HOME/.kube
            sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
            sudo chown $(id -u):$(id -g) $HOME/.kube/config
            ```
    - Initializing the `192.168.0.234` master node
        1. Remove the `apiserver.crt` and `apiserver.key`.
            ```
            $ rm ~/pki/apiserver.*
            ```
        2. Move the certificates to the `/etc/kubernetes` directory.
            ```
            $ sudo mv ~/pki /etc/kubernetes/
            ```
        3. Create the configuration file for `kubeadm`.
            ```
            $ nano config.yaml
            apiVersion: kubeadm.k8s.io/v1beta1
            kind: MasterConfiguration
            tokenTTL: “0”
            ---
            apiVersion: kubeadm.k8s.io/v1beta1
            kind: ClusterConfiguration
            kubernetesVersion: stable
            apiServer:
                certSANs:
                    - 192.168.0.222
            controlPlaneEndpoint: "192.168.0.222:6443"
            etcd:
                external:
                    endpoints:
                        - https://192.168.0.123:2379
                        - https://192.168.0.234:2379
                    caFile: /etc/etcd/ca.pem
                    certFile: /etc/etcd/kubernetes.pem
                    keyFile: /etc/etcd/kubernetes-key.pem
            ```
        4. Initialize the machine as a master node.
            ```
            $ sudo kubeadm init --config=config.yaml	
            ```
        5. Setup `kubeconfig`
            ```
            mkdir -p $HOME/.kube
            sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
            sudo chown $(id -u):$(id -g) $HOME/.kube/config
            ```
    - Initializing the worker nodes
        1. Execute the "kubeadm join" command that you copied from the last step of the initialization of the masters on each worker node.
            ```
            $ sudo kubeadm join 192.168.0.222:6443 --token 1g1njb.ul5eu1b9h3ebqp3g \
                --discovery-token-ca-cert-hash sha256:250d64c06ed2c8f71c895441d5facb560abba1abc8904c537d8006c8fb8d3337
            ```
    - Configuring `kubectl` on the client machine(Loadbalancer)
        1. SSH to one of the master node.
            ```
            $ ssh sguyennet@192.168.0.123
            ```
        2. Add permissions to the `admin.conf` file.
            ```
            $ sudo chmod +r /etc/kubernetes/admin.conf
            ```
        3. From the client machine, copy the configuration file.
            ```
            $ scp sguyennet@192.168.0.123:/etc/kubernetes/admin.conf .
            ```
        4. Create the kubectl configuration directory.
            ```
            $ mkdir ~/.kube
            ```
        5. Move the configuration file to the configuration directory.
            ```
            $ mv admin.conf ~/.kube/config
            ```
        6. Modify the permissions of the configuration file.
            ```
            $ chmod 600 ~/.kube/config
            ```
        7. Go back to the SSH session on the master and change back the permissions of the configuration file.
            ```
            $ sudo chmod 600 /etc/kubernetes/admin.conf
            ```
        8. check that you can access the Kubernetes API from the client machine.
            ```
            $ kubectl get nodes
            ```
    - Deploying the overlay network
        1. Install weave-net network driver on master node
            ```
            kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
            ```
7. On the master and all the workers run the following command
    ```
    $ sudo sysctl net.bridge.bridge-nf-call-iptables=1
    ```
## How to deploy App `softdef-rps`
1. write `build.sh` for building and uploading the app to `dockerhub`
    ```
    docker build -t {DOCKER_USER}/softdef-rps-front front/
    docker build -t {DOCKER_USER}/softdef-rps-user user/
    docker build -t {DOCKER_USER}/softdef-rps-back back/
    docker build -t {DOCKER_USER}/softdef-rps-bot bot/

    docker push {DOCKER_USER}/softdef-rps-front
    docker push {DOCKER_USER}/softdef-rps-user
    docker push {DOCKER_USER}/softdef-rps-back
    docker push {DOCKER_USER}/softdef-rps-bot
    ```
2. write `deploy.sh` to automatically clean all existing deployment, pods, and services and deploy new version of the app
    ```
    kubectl delete deployment,pods,services -l app=rps
    echo sleep 20 secs
    sleep 20  # set some delay to make sure all resources are freed

    kubectl apply -f user-service.yaml
    kubectl apply -f back-service.yaml
    kubectl apply -f bot-service.yaml
    kubectl apply -f front-service.yaml
    ```
3. make them executable
    ```
    $ chmod +x *.sh
    ```
4. write deployment configuration for each service
    - `back-service.yaml`
        ```
        ---
        apiVersion: v1
        kind: Service
        metadata:
          name: back-service
          labels:
            app: rps
        spec:
          ports:
            - port: 5002
              protocol: TCP
              targetPort: 5002
          selector:
            app: rps
            tier: back
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: back-service
          labels:
            app: rps
        spec:
          replicas: 2
          strategy:
            type: Recreate
          selector:
            matchLabels:
              app: rps
              tier: back
          template:
            metadata:
              labels:
                app: rps
                tier: back
            spec:
              containers:
                - image: {DOCKER_USER}/softdef-rps-back:latest
                  name: back-service
                  ports:
                    - containerPort: 5002
              tolerations:
              - key: "node.kubernetes.io/not-ready"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
              - key: "node.kubernetes.io/unreachable"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
        ```
    - `bot-service.yaml`
        ```
        ---
        apiVersion: v1
        kind: Service
        metadata:
          name: bot-service
          labels:
            app: rps
        spec:
          ports:
            - port: 5003
              protocol: TCP
              targetPort: 5003
          selector:
            app: rps
            tier: bot
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: bot-service
          labels:
            app: rps
        spec:
          replicas: 2
          strategy:
            type: Recreate
          selector:
            matchLabels:
              app: rps
              tier: bot
          template:
            metadata:
              labels:
                app: rps
                tier: bot
            spec:
              containers:
                - image: {DOCKER_USER}/softdef-rps-bot:latest
                  name: bot-service
                  ports:
                    - containerPort: 5003
              tolerations:
              - key: "node.kubernetes.io/not-ready"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
              - key: "node.kubernetes.io/unreachable"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
        ```
    - `front-service.yaml`
        ```
        ---
        apiVersion: v1
        kind: Service
        metadata:
          name: front-service
          labels:
            app: rps
        spec:
          type: NodePort
          ports:
            - port: 5000
              protocol: TCP
              targetPort: 5000
              nodePort: 30001
          selector:
            app: rps
            tier: front
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: front-service
          labels:
            app: rps
        spec:
          replicas: 2
          strategy:
            type: Recreate
          selector:
            matchLabels:
              app: rps
              tier: front
          template:
            metadata:
              labels:
                app: rps
                tier: front
            spec:
              containers:
                - image: {DOCKER_USER}/softdef-rps-front:latest
                  imagePullPolicy: Always
                  name: front-service
                  ports:
                    - containerPort: 5000
              tolerations:
              - key: "node.kubernetes.io/not-ready"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
              - key: "node.kubernetes.io/unreachable"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
        ```
    - `user-service.yaml`
        ```
        ---
        apiVersion: v1
        kind: Service
        metadata:
          name: user-service
          labels:
            app: rps
        spec:
          ports:
            - port: 5001
              protocol: TCP
              targetPort: 5001
          selector:
            app: rps
            tier: user
        ---
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: user-service
          labels:
            app: rps
        spec:
          replicas: 2
          strategy:
            type: Recreate
          selector:
            matchLabels:
              app: rps
              tier: user
          template:
            metadata:
              labels:
                app: rps
                tier: user
            spec:
              containers:
                - image: {DOCKER_USER}/softdef-rps-user:latest
                  name: user-service
                  ports:
                    - containerPort: 5001
              tolerations:
              - key: "node.kubernetes.io/not-ready"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
              - key: "node.kubernetes.io/unreachable"
                operator: "Exists"
                effect: "NoExecute"
                tolerationSeconds: 10
        ```
5. execute the scripts to build and deploy
    ```
    $ ./build.sh
    $ ./deploy.sh
    ```
# Start the app
1. write `start.sh` on one of the master nodes to find the IP of the running app and browse to the IP on `google chrome`
    ```
    google-chrome $(kubectl get svc | grep front | awk '{print $3}'):5000
    ```
2. make it executable
    ```
    $ chmod +x start.sh
    ```
3. execute `start.sh`
    ```
    $ ./start.sh
    ```
