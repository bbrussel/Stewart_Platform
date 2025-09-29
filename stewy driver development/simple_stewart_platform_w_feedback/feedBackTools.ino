
void printReceivedInputs() {
    Serial.print(inputFloats[0]);
    Serial.print(",");
    Serial.print(inputFloats[1]);
    Serial.print(",");
    Serial.print(inputFloats[2]);
    Serial.print(",");
    Serial.print(inputFloats[3]);
    Serial.print(",");
    Serial.print(inputFloats[4]);
    Serial.print(",");
    Serial.println(inputFloats[5]);
}


void recvWithEndMarker() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;
    
    while (Serial.available() > 0 && newInputCommand == false) {
        rc = Serial.read();
        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0'; // terminate the string
            ndx = 0;
            newInputCommand = true;
        }
    }
}

void showNewData() {
    if (newInputCommand == true) {
        Serial.print("This just in ... ");
        Serial.println(receivedChars);
        newInputCommand = false;
    }
}