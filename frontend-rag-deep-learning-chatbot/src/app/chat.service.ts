import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  sendQuery(query: string): Observable<string> {
    return new Observable(observer => {
      fetch('/api/query/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query}),
      })
      .then(response => {
        const reader = response.body?.getReader();
        if(!reader) {
          observer.error(new Error("Failed to get reader from the response body"));
          return;
        }

        const decoder = new TextDecoder();
        const readStream = () => {
		reader.read().then(({ done, value }) => {
            if (done) {
              observer.complete();
              return;
            }

	    const chunk = decoder.decode(value , {stream: true});
	    if (chunk.includes("[heartbeat]")){
        console.log("Recieved heartbeat...")
      } else {
        observer.next(chunk);
      }
	    readStream();
	}).catch(error => observer.error(error));
	};
	readStream();
    })
    .catch(error => observer.error(error));
    });
}
}
