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
      this.chatService.sendQuery(this.newMessage.trim()).subscribe(
        (response) => {
          this.messages.push({ text: response.answer, isUser: false }); // Odgovor agenta
          console.log('odgovor agenta');
        },
        (error) => {
          console.error('Error fetching response:', error);
          this.messages.push({ text: 'Error: Unable to fetch response.', isUser: false });
        }
      );
      this.newMessage = '';
      
     // setTimeout(() => {
     //   this.messages.push({ text: 'This is a response from the agent.', isUser: false });
     // }, 1000);
    }
  }

  
  
  uploadFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      console.log('File uploaded:', file);

      this.fileService.uploadFile(file).subscribe(
        (response) => {
          console.log(response);
        },
        (error) => {
          console.error('Error during file upload:', error);
        }
      );
    }

  }
  
}

