#include "tcpSocket.hpp"

tcpSocket::tcpSocket(int port)
{
	m_sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if(m_sockfd < 0)
	{
		printf("Socket connection failed..\n");
		//exit(0);
	}

	m_servaddr.sin_family = AF_INET;
	m_servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	m_servaddr.sin_port = htons(port);

	if ((bind(m_sockfd, (struct sockaddr *) &m_servaddr, sizeof(m_servaddr))) != 0)
		{
        printf("socket bind failed...\n");
        //exit(0);
    }

	if ((listen(m_sockfd, 5)) != 0)
		{
        printf("Listen failed...\n");
        //exit(0);
    }
	uint len = sizeof(m_cliaddr);
	m_connfd = accept(m_sockfd, (struct sockaddr *) &m_cliaddr, &len);

	if (m_connfd < 0)
		printf("server acccept failed...\n");

}

tcpSocket::~tcpSocket()
{
	close(m_sockfd);
}

void tcpSocket::receive(char *buf)
{
	read(m_connfd, buf, sizeof(buf));
}

void tcpSocket::send(const char *buf)
{
	write(m_connfd, buf, sizeof(buf));
}

void tcpSocket::send(double *buf)
{
	char buffer[MAXLINE];
	sprintf(buffer, "%f", *buf);
	send(buffer);
	send("\n");
}
