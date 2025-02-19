// Script with all the predefined pipeline jobs.

pipelineJob('hadoop-test') {
  definition {
    cps {
      script(readFileFromWorkspace('/var/jenkins_home/pipelines/Jenkinsfile.hadoop'))
      sandbox(true)
    }
  }
}

pipelineJob('hadoop-test-custom-spans') {
  definition {
    cps {
      script(readFileFromWorkspace('/var/jenkins_home/pipelines/Jenkinsfile.hadoop.custom.spans'))
      sandbox(true)
    }
  }
}

pipelineJob('test-custom-spans') {
  definition {
    cps {
      script(readFileFromWorkspace('/var/jenkins_home/pipelines/Jenkinsfile.test.spans'))
      sandbox(true)
    }
  }
}

pipelineJob('test-spans-poc') {
  definition {
    cps {
      script(readFileFromWorkspace('/var/jenkins_home/pipelines/Jenkinsfile.poc'))
      sandbox(true)
    }
  }
}

