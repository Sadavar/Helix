import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Chat from './Chat/Chat';
import { Message, Sequence } from '../types/types';
import { socket } from '../socket';
import Workspace from './Workspace/Workspace';

export default function MainScreen() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [sequence, setSequence] = useState<Sequence[]>([]);
    const [isConnected, setIsConnected] = useState(socket.connected);
    const [input, setInput] = useState('');
    const { state } = useLocation();
    const { username } = state;

    useEffect(() => {
        function onConnect() {
            setIsConnected(true);
            console.log(socket)
            console.log('Connected with username:', username);
        }

        function onDisconnect() {
            setIsConnected(false);
            console.log('Disconnected');
        }

        function onAllMessages(data: any) {
            console.log("received messages for", username, data);
            const messages: Message[] = data.map((msg: any) => ({
                sender: msg[0],
                reciever: msg[1],
                content: msg[2],
                timestamp: msg[3],
            }));
            setMessages(messages);
        }

        function onSequence(data: any) {
            console.log("received sequence for", username, data);
            const sequenceList: Sequence[] = data.map((seq: any) => ({
                step_number: seq.step_number,
                content: seq.content,
            }));
            console.log(sequenceList)
            setSequence(sequenceList);
        }

        socket.emit('join_room', { username })

        // Set up connection listeners
        socket.on('connect', onConnect);
        socket.on('all-messages', onAllMessages);
        socket.on('sequence', onSequence);

        // Request initial data
        socket.emit('get_all_messages', { username });
        socket.emit('get_sequence', { username });

        // Cleanup function
        return () => {
            socket.off('connect', onConnect);
            socket.off('disconnect', onDisconnect);
            socket.off('all-messages', onAllMessages);
            socket.off('sequence', onSequence);
        };
    }, [username]);

    const handleSend = () => {
        if (input.trim()) {
            // Send user message to the server
            console.log(socket)
            console.log("sending")
            socket.emit('user-query', { username: username, query: input });
            setInput('');  // Clear input field
        }
    };

    return (
        <div style={{ display: 'flex', width: '100vw', height: '100vh' }}>
            <div style={{ display: 'flex', flexDirection: 'column', width: '40%', height: '99%', borderRadius: '15px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', padding: '20px' }}>
                <h1>Chat</h1>
                <Chat messages={messages} setMessages={setMessages} />
                <div>
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        onKeyDown={(e) => e.key === 'Enter' ? handleSend() : null}
                        style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', height: '10%' }}
                    />
                    <button onClick={handleSend} style={{ marginTop: '10px', padding: '10px 20px', borderRadius: '5px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>Send</button>
                </div>
            </div>
            <div style={{ width: '60%', borderRadius: '15px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', padding: '20px', margin: '10px', backgroundColor: 'white' }}>
                <h1>Workspace</h1>
                <Workspace sequence={sequence} />
            </div>
        </div >
    );
}