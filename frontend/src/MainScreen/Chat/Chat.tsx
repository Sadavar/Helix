import React, { useState, useEffect, useRef, createRef } from 'react';
import { io } from 'socket.io-client';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Message } from '../../types/types';

function AllMessages({ messages, username }: { messages: Message[], username: string }) {
    function IndividualChatMessage({ msg }: { msg: Message }) {
        let sender = msg.sender === 1 ? 'AI' : username;
        let isAI = msg.sender === 1;

        const messageStyle = {
            display: 'flex',
            justifyContent: isAI ? 'flex-start' : 'flex-end',
            marginBottom: '10px'
        };

        const bubbleStyle = {
            maxWidth: '60%',
            padding: '10px',
            borderRadius: '10px',
            backgroundColor: isAI ? '#e0e0e0' : '#0084ff',
            color: isAI ? '#000' : '#fff',
            textAlign: 'left'
        };

        return (
            <div style={messageStyle}>
                <div style={bubbleStyle}>
                    <strong>{sender}:</strong> {msg.content}
                </div>
            </div>
        );
    }

    const messageStyle = {
        display: 'flex',
        justifyContent: 'flex-start',
        marginBottom: '10px',
        marginTop: '10px'
    };

    const bubbleStyle = {
        maxWidth: '60%',
        padding: '10px',
        borderRadius: '10px',
        backgroundColor: '#e0e0e0',
        color: '#000',
        textAlign: 'left'
    };

    if (messages.length > 0) {
        const messageList = messages.map((msg: Message, index: number) => (
            <IndividualChatMessage key={index} msg={msg} />
        ));

        return <div>{messageList}</div>;
    } else {
        return (
            <div style={messageStyle}>
                <div style={bubbleStyle}>
                    <strong>AI:</strong> Hello, how can I help you?
                </div>
            </div>
        )
    }
}

export default function Chat({ messages, setMessages }: { messages: Message[], setMessages: React.Dispatch<React.SetStateAction<Message[]>> }) {

    const { state } = useLocation();
    const { username } = state;

    const chatContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const chatContainerStyle = {
        display: 'flex',
        flexDirection: 'column',
        height: '80%',
        boxSizing: 'border-box'
    };

    const chatHistoryStyle = {
        flex: 1,
        overflowY: 'auto',
        marginBottom: '20px'
    };

    return (
        <div style={chatContainerStyle}>
            <div ref={chatContainerRef} style={chatHistoryStyle}>
                <AllMessages messages={messages} username={username} />
            </div>
        </div>
    );
}
