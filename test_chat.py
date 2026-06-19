import unittest
from unittest.mock import MagicMock, patch
import chat
import socket
import ssl

class TestChatServer(unittest.TestCase):

    def setUp(self):
    
        chat.connected_clients.clear()

    def test_broad_cast(self):
        mock_socket = MagicMock()
        chat.connected_clients["user1"] = mock_socket
        
        chat.broad_cast(b"hello world")
        
        mock_socket.send.assert_called_with(b"hello world")

    def test_broad_cast_exclude_sender(self):
        mock_socket_sender = MagicMock()
        mock_socket_other = MagicMock()
        chat.connected_clients["sender"] = mock_socket_sender
        chat.connected_clients["other"] = mock_socket_other
        
        chat.broad_cast(b"hello", sender_nickname="sender")
        
        mock_socket_sender.send.assert_not_called()
        mock_socket_other.send.assert_called_with(b"hello")

    def test_remove_client(self):
        mock_socket = MagicMock()
        chat.connected_clients["user1"] = mock_socket
        
        chat.remove_client("user1", mock_socket)
        
        self.assertNotIn("user1", chat.connected_clients)
        mock_socket.close.assert_called_once()

    @patch('chat.broad_cast')
    def test_handle_graceful_disconnect(self, mock_broadcast):
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""  
        
        chat.handle(mock_socket, "user1")
        
    
        mock_socket.close.assert_called()

    @patch('chat.broad_cast')
    def test_handle_message_too_long(self, mock_broadcast):
        mock_socket = MagicMock()
    
        mock_socket.recv.side_effect = [b"a" * 600, b""] 
        
        chat.handle(mock_socket, "user1")
        
        mock_socket.send.assert_called_with("Message too long. Max 512 bytes.".encode('ascii'))
        mock_broadcast.assert_not_called()

    @patch('chat.ssl_server_socket')
    @patch('chat.handle')
    def test_receive(self, mock_handle, mock_server_socket):
        mock_client_socket = MagicMock()
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))
        
        mock_client_socket.recv.return_value = b"TestUser"
        
        mock_server_socket.accept.side_effect = [ (mock_client_socket, ('127.0.0.1', 12345)), Exception("Stop Loop")]
        
        with self.assertRaises(Exception):
            chat.receive()
        
        self.assertIn("TestUser", chat.connected_clients)

if __name__ == '__main__':
    unittest.main()