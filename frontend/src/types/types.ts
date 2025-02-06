export interface Message {
    sender: number
    reciever: number
    content: string
    timestamp: Date
}

export interface Sequence {
    step_number: number
    content: string
}
