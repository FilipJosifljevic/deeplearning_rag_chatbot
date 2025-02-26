import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apiUrl = '/api/query/';

  constructor(private http: HttpClient) {}

  sendQuery(query: string): Observable<any> {
    return new Observable(observer =>  {
    fetch(this.apiUrl, {
    	method: 'POST',
    	headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    })
    .then(response => {
    	const reader = response.body?.getReader();
	const decoder = new TextDecoder();

	if (!reader) {
		observer.error('No response body');
		return;
	}
	const readStream = () => {
		reader.read().then(({ done, value }) => {
            if (done) {
              observer.complete();
              return;
            }

	    const chunk = decoder.decode(value , {stream: true});
	    observer.next(chunk);
	    readStream();
	}).catch(error => observer.error(error));
	};
	readStream();
    })
    .catch(error => observer.error(error));
    });
}
}
