FROM python:3.13

# Create working directory
RUN mkdir -p /src
WORKDIR /src

# Copy source code to the container
COPY src/ /src/

# Install Poetry
RUN pip install poetry==2.1.1

# Configure Poetry to not create virtual environments and install dependencies
RUN poetry config virtualenvs.create false && poetry install

# Expose port 80
EXPOSE 8787

# Copy bash configuration for terminal colors
COPY docker/.bashrc /root/.bashrc

# Prepare the CMD command with the script to be run at the begining of the deploy
RUN mkdir -p /scripts
COPY docker/post_deploy.sh /scripts/post_deploy.sh

CMD /scripts/post_deploy.sh
