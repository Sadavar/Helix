import { useEffect, useRef } from "react";
import { Sequence } from "../../types/types";



export default function Workspace({ sequence }: { sequence: Sequence[] }) {

    const workspaceContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (workspaceContainerRef.current) {
            workspaceContainerRef.current.scrollTop = workspaceContainerRef.current.scrollHeight;
        }
    }, [sequence]);

    function IndividualStep({ msg }: { msg: Sequence }) {
        console.log(msg)
        return (
            <div style={{ display: 'flex', flexDirection: 'column', borderRadius: '15px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', padding: '20px', margin: '10px', backgroundColor: 'white' }}>
                <strong>Step {msg.step_number}</strong>
                <p>{msg.content}</p>
            </div>
        );
    }

    if (sequence.length > 0) {
        const stepList = sequence.map((msg: Sequence) => (
            <IndividualStep key={msg.step_number} msg={msg} />
        ));

        return (
            <div ref={workspaceContainerRef} style={{ height: '85%', display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
                {stepList}
            </ div>
        )
    } else {
        return <h2></h2>;
    }
}