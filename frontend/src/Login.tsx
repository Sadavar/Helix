import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";


export default function Login() {
    const [username, setUsername] = useState("")
    const [input, setInput] = useState('');
    const navigate = useNavigate();

    function handleSend() {
        setUsername(input)
        return navigate("/chat", { state: { username: input } });
    }

    return (
        <>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f0f0f0' }}>
                <h1 style={{ marginBottom: '20px', color: '#333' }}> Please Login </h1>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your username..."
                    onKeyDown={(e) => e.key === 'Enter' ? handleSend() : null}
                    style={{ padding: '10px', fontSize: '16px', marginBottom: '10px', borderRadius: '5px', border: '1px solid #ccc', width: '300px' }}
                />
                <button
                    onClick={handleSend}
                    style={{ padding: '10px 20px', fontSize: '16px', borderRadius: '5px', border: 'none', backgroundColor: '#007bff', color: '#fff', cursor: 'pointer' }}
                >
                    Send
                </button>
            </div>
        </>
    )
}