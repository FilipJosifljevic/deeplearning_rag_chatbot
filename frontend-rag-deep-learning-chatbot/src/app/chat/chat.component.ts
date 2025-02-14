import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../chat.service';
import { FileService } from '../file.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
})
export class ChatComponent {
  messages: { text: string; isUser: boolean }[] = [];
  newMessage: string = '';

  constructor(private chatService: ChatService, private fileService: FileService) {}

  sendMessage(): void {
    if (this.newMessage.trim()) {
      this.messages.push({ text: this.newMessage, isUser: true });

      let botResponse = { text: '', isUser: false };
      this.messages.push(botResponse);

      this.chatService.sendQuery(this.newMessage.trim()).subscribe({
        next: (chunk: string) => {
          botResponse.text += chunk; // Append tokens live
        },
        error: (error: any) => {
          console.error('Error fetching response:', error);
          botResponse.text = 'Error: Unable to fetch response.';
        }
      });

      this.newMessage = ''; // Clear input field
    }
  }

  
  
  uploadFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input && input.files && input.files.length > 0) {
      const file = input.files[0];
      console.log('File uploaded:', file);

      this.fileService.uploadFile(file).subscribe({
        next : (response) => {
          console.log(response);
        },
        error : (error: any) => {
          console.error('Error during file upload:', error);
        }
      });
    }

  }
  
}

