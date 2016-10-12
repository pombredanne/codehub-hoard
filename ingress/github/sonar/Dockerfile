FROM java:8

MAINTAINER Nate Solomon <solomon_nathaniel@bah.com>

ENV SONAR_VERSION=6.1 \
    SONARQUBE_HOME=/opt/sonarqube \
    # Database configuration
    # Defaults to using H2
    SONARQUBE_JDBC_USERNAME=sonar \
    SONARQUBE_JDBC_PASSWORD=sonar \
    SONARQUBE_JDBC_URL=

# Http port
EXPOSE 9000

RUN set -x \

    # pub   2048R/D26468DE 2015-05-25
    #       Key fingerprint = F118 2E81 C792 9289 21DB  CAB4 CFCA 4A29 D264 68DE
    # uid                  sonarsource_deployer (Sonarsource Deployer) <infra@sonarsource.com>
    # sub   2048R/06855C1D 2015-05-25
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys F1182E81C792928921DBCAB4CFCA4A29D26468DE \

    && cd /opt \
    && curl -o sonarqube.zip -fSL https://sonarsource.bintray.com/Distribution/sonarqube/sonarqube-$SONAR_VERSION.zip \
    && curl -o sonarqube.zip.asc -fSL https://sonarsource.bintray.com/Distribution/sonarqube/sonarqube-$SONAR_VERSION.zip.asc \
    && gpg --batch --verify sonarqube.zip.asc sonarqube.zip \
    && unzip sonarqube.zip \
    && mv sonarqube-$SONAR_VERSION sonarqube \
    && rm sonarqube.zip* \
    && rm -rf $SONARQUBE_HOME/bin/*

RUN cd $SONARQUBE_HOME/extensions/plugins \
    && curl -o sonar-java-plugin-4.2.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-java-plugin/sonar-java-plugin-4.2.jar \
    && curl -o sonar-javascript-plugin-2.15.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-javascript-plugin/sonar-javascript-plugin-2.15.jar \
    && curl -o sonar-csharp-plugin-5.3.2.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-csharp-plugin/sonar-csharp-plugin-5.3.2.jar \
    && curl -o sonar-python-plugin-1.6.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-python-plugin/sonar-python-plugin-1.6.jar \
    && curl -o sonar-groovy-plugin-1.3.1.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-groovy-plugin/sonar-groovy-plugin-1.3.1.jar \
    && curl -o sonar-ldap-plugin-1.5.1.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-ldap-plugin/sonar-ldap-plugin-1.5.1.jar \
    && curl -o sonar-php-plugin-2.7.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-php-plugin/sonar-php-plugin-2.7.jar \
    && curl -o sonar-xml-plugin-1.3.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-xml-plugin/sonar-xml-plugin-1.3.jar \
    && curl -o sonar-web-plugin-2.4.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-web-plugin/sonar-web-plugin-2.4.jar \
    && curl -o sonar-scm-git-plugin-1.2.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-scm-git-plugin/sonar-scm-git-plugin-1.2.jar \
    && curl -o sonar-scm-svn-plugin-1.3.jar -fSL http://sonarsource.bintray.com/Distribution/sonar-scm-svn-plugin/sonar-scm-svn-plugin-1.3.jar

VOLUME ["$SONARQUBE_HOME/data", "$SONARQUBE_HOME/extensions"]

WORKDIR $SONARQUBE_HOME
COPY docker-entrypoint.sh $SONARQUBE_HOME/bin/
RUN chmod +x $SONARQUBE_HOME/bin/docker-entrypoint.sh
ENTRYPOINT ["./bin/docker-entrypoint.sh"]
