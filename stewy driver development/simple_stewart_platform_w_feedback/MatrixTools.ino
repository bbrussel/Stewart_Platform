void printArray(float array[], int len) {
    Serial.print("[");
    for(int i = 0; i < len; i++) {
        Serial.print(array[i], 10);
        if (i < len - 1) {
            Serial.print(", ");
        }
    }
    Serial.println("]");
}

void printNx3Array(float array[][3], int numRows) {
    for (int i = 0; i < numRows; i++) {
        for (int j = 0; j < 3; j++) {
            Serial.print(array[i][j], 10);
            if (j < 2) {
                Serial.print(", ");
            }
        }
        Serial.println();
    }
}


void printNx6Array(float array[][6], int numRows) {
    for (int i = 0; i < numRows; i++) {
        for (int j = 0; j < 6; j++) {
            Serial.print(array[i][j], 10);
            if (j < 5) {
                Serial.print(", ");
            }
        }
        Serial.println();
    }
}

void matrixMultiply3x3(float a[3][3], float b[3][3], float result[3][3]) {
  // Initialize all elements of result matrix to 0
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      result[i][j] = 0;
    }
  }

  // Perform the matrix multiplication
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      for (int k = 0; k < 3; k++) {
        result[i][j] += a[i][k] * b[k][j];
      }
    }
  }
}

void matrixMultiply3x3_3x6(float a[3][3], float b[3][6], float result[3][6]) {
  // Initialize all elements of result matrix to 0
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 6; j++) {
      result[i][j] = 0;
    }
  }

  // Perform the matrix multiplication
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 6; j++) {
      for (int k = 0; k < 3; k++) {
        result[i][j] += a[i][k] * b[k][j];
      }
    }
  }
}

void transposeMatrix6x3(float a[6][3], float result[3][6]) {
  // Transpose a 6x3 matrix
  for (int i = 0; i < 6; i++) {
    for (int j = 0; j < 3; j++) {
      result[j][i] = a[i][j];
    }
  }
}
