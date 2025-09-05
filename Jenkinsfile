pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Vipul-0722/jenkins_starter.git',
                    credentialsId: 'ecf815ab-0b0f-442a-9767-d2b76edddaf6'
            }
        }
        stage('Build') {
            steps {
                sh 'echo Building app...'
                sh 'python3 --version || python --version'
                sh 'python3 app.py || python app.py'
            }
    }
        stage('Test') {
            steps {
                sh 'echo Running tests...'
                sh 'python3 -m unittest test_app.py'
            }
        }
    }
}
