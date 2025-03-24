import { Component, ChangeDetectorRef } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser'
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../chat.service';
import { FileService } from '../file.service';
import { DividerModule } from 'primeng/divider';
import { ButtonModule } from 'primeng/button'
import { InputTextModule } from 'primeng/inputtext';
import { FileUploadModule } from 'primeng/fileupload';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
@Component({
    selector: 'app-chat',
    imports: [CommonModule, FormsModule, ButtonModule, MessageModule, DividerModule, InputTextModule, FileUploadModule, CardModule, ScrollPanelModule],
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  messages: { text: string; isUser: boolean }[] = [];
  newMessage: string = '';

  constructor(private chatService: ChatService, private fileService: FileService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.messages.push({ text: 'Welcome! How can I help you today?', isUser: false });
  }
  sendMessage(): void {
    if (this.newMessage.trim()) {
      this.messages.push({ text: this.newMessage, isUser: true });

      let botResponse = { text: '', isUser: false };
      this.messages.push(botResponse);

      this.chatService.sendQuery(this.newMessage.trim()).subscribe({
        next: (chunk: string) => {
          botResponse.text += chunk;
	        this.cdr.detectChanges(); // Append tokens live
        },
        error: (error: any) => {
          console.error('Error fetching response:', error);
          botResponse.text = 'Error: Unable to fetch response.';
	        this.cdr.detectChanges();
        }
      });

      this.newMessage = ''; // Clear input field
    }
  }



  uploadFile(event: any): void {
     if (event.files && event.files.length > 0) {
      const file = event.files[0];
      this.processUploadedFile(file);
    }
    // For traditional file input
    else if (event.target && event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      this.processUploadedFile(file);
    }
  }

  private processUploadedFile(file: File): void {
    console.log('File uploaded:', file);

    // Add a message about the file
    this.messages.push({
      text: `Uploading file: ${file.name}`,
      isUser: true
    });

    // Use the file service
    this.fileService.uploadFile(file).subscribe({
      next: (response) => {
        console.log(response);
        // Add response message if needed
        this.messages.push({
          text: `File uploaded successfully. Processing ${file.name}...`,
          isUser: false
        });
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Error during file upload:', error);
        this.messages.push({
          text: `Error uploading file: ${error.message || 'Unknown error'}`,
          isUser: false
        });
        this.cdr.detectChanges();
      }
    });
  }

}

