FROM jenkins/agent

USER root
RUN apt update --fix-missing \
    && apt -y install \
                python3 \
                python3-pip \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && echo \
        "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list > /dev/null \
    && apt update \
    && apt -y install \
                docker-ce \
                docker-ce-cli \
                containerd.io \
                kubectl \
    && usermod -aG docker jenkins

USER ${user}
RUN pip install pylint # pipreqs pip-tools

CMD ["bash"]
