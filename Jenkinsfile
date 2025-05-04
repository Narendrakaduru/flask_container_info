pipeline {
    agent none
    environment {
        IMAGE_NAME = "narendra8686/flask-container-info"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Git clone') {
            agent { label 'vldocsrv091' }
            steps {
                git branch: 'main', credentialsId: 'Git_Auth', url: 'https://github.com/Narendrakaduru/flask_container_info.git'
            }
        }

        stage('Run Bandit Scan') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '-u root -v $WORKSPACE:/workspace'  // Mount the Jenkins workspace to a container directory
                    reuseNode true   // Reuse the workspace from the previous stage
                }
            }
            steps {
                sh '''
                    pip install --no-cache-dir bandit
                    bandit -r -lll -iii . -f json | tee /workspace/bandit-report.json
                '''
            }
        }
        
        stage('Upload Bandit scan Results') {
            agent { label 'vldocsrv091' }
            steps {
                sh '''
                    pip install python-dotenv
                    cd "$WORKSPACE"
                    python3 upload_to_defectdojo.py
                '''
            }
        }
        
        stage('Build Docker Image') {
            agent { label 'vldocsrv091' }
            steps {
				sh """
					echo "🐳 Building Docker image..."
					docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
					docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
					echo "✅ Built Image successfully!"
				"""
            }
        }
        
        stage('Docker Scout Scan') {
            agent { label 'vldocsrv091' }
                steps {
                    ansiColor('gnome-terminal') {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub_credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                            docker run --rm -u root -v /var/run/docker.sock:/var/run/docker.sock \
                                -e DOCKER_SCOUT_HUB_USER=\$DOCKER_USER \
                                -e DOCKER_SCOUT_HUB_PASSWORD=\$DOCKER_PASS \
                                docker/scout-cli quickview ${IMAGE_NAME}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }
        
        stage('Push Docker Image') {
            agent { label 'vldocsrv091' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker_hub_credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "🔐 Logging in to Docker Hub..."
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        
                        echo "📤 Pushing Docker image..."
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
        
                        echo "✅ Image pushed successfully!"
                    """
                }
            }
        }
        
        stage('Update Helm Manifest with Build Number') {
          agent { label 'vldocsrv091' }
          environment {
            GIT_REPO = 'https://github.com/Narendrakaduru/flask_container_info_manifests.git'
            CREDENTIALS_ID = 'Git_Auth'
          }
          steps {
            withCredentials([usernamePassword(credentialsId: "${CREDENTIALS_ID}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
              sh '''
                echo "Removing Existing Repo"
                rm -rf ./flask_container_info_manifests
                echo "Cloning repo..."
                git clone https://github.com/Narendrakaduru/flask_container_info_manifests.git
        
                cd flask_container_info_manifests
                git config --global --add safe.directory `pwd`
        
                echo "Updating tag with BUILD_NUMBER ${BUILD_NUMBER}..."
                sed -i "s/^  tag: .*/  tag: ${BUILD_NUMBER}/" values.yaml
        
                git add values.yaml
                git commit -m "Jenkins updated image tag : ${BUILD_NUMBER}"
                git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/Narendrakaduru/flask_container_info_manifests.git
                git push origin main
              '''
            }
          }
        }
        
        stage('Sync to ArgoCD') {
            agent { label 'vldocsrv091' }
            steps {
                script {
                    try {
                        echo "🔄 Syncing to ArgoCD..."
                        sh '''
                        # Check if the script exists
                        ls -l $WORKSPACE
                        cd $WORKSPACE
                        # Make sure the script is executable
                        chmod +x ./sync_flask_container_info_manifests.sh
                        sudo ./sync_flask_container_info_manifests.sh
                        '''
                        echo "✅ Successfully synced to ArgoCD!"
                    } catch (Exception e) {
                        echo "❌ ArgoCD sync failed: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("ArgoCD sync failed.")
                    }
                }
            }
        }

		
    }
}
