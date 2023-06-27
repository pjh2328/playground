plugins {
    id("java")
}

group = "io.conduktor.demos"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {

    // https://mvnrepository.com/artifact/org.apache.kafka/kafka-clients
    implementation 'org.apache.kafka:kafka-clients:3.5.0'

    // https://mvnrepository.com/artifact/org.slf4j/slf4j-api
    implementation 'org.slf4j:slf4j-api:2.0.7'

    // https://mvnrepository.com/artifact/org.slf4j/slf4j-simple
    Implementation 'org.slf4j:slf4j-simple:2.0.7'

}

tasks.test {
    useJUnitPlatform()
}