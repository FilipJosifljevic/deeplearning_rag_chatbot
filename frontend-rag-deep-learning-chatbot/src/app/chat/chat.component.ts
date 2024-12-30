import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

  sendMessage(): void {
    if (this.newMessage.trim()) {
      this.messages.push({ text: this.newMessage, isUser: true });
      this.newMessage = '';

      // Simulate agent response
      setTimeout(() => {
        this.messages.push({ text: 'This is a response from the agent.', isUser: false });
      }, 1000);
    }
  }

  uploadFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      console.log('File uploaded:', file);

      // Here, send the file to the backend as needed
    }
  }
}
