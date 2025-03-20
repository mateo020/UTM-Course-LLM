export interface ChatMessageType{
    files: File[];
    message: string;
    date: Date;
    user_id: number;
    suggestions: string[];
}

export interface HistoryChatType {
    message: string;
    is_user: boolean;
    file_name: string;
    date: Date;
    user_id: number;
    files?: FileWithType[];
}

export interface SubTask {
    title: string;
    description: string;
}

export interface FileWithType extends File {
    fileType?: 'instructional' | 'supplementary';
}