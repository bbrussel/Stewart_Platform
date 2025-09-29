#include<stdio.h>
#include <string.h>
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()

int main() {

	int serial_port = open("/dev/ttyACM0", O_RDWR);

	char read_buf [256];

	if (serial_port < 0) {
		printf("Error %i from open: %s\n", errno, strerror(errno));
	} else {

		unsigned char msg[] = { '2', '2', '\r' };

		write(serial_port, msg, sizeof(msg));
		sleep(1);

		int n = read(serial_port, &read_buf, sizeof(read_buf));

		printf("%s",read_buf);

		close(serial_port);
	}
}
