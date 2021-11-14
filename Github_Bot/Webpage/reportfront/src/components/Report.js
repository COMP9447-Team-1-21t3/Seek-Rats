import logo from '../logo.svg';
import '../App.css';
import React, { useEffect, useState } from "react";
import url from './config.txt';
import update_url from './config2.txt';
import axios from "axios";

function Report({auth_url_json}) {

    // const [secrets, setSecrets] = useState([{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
    // {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}])

    const [token, setToken] = useState("")
    const [ready, setReady] = useState(false)
    const [error, setError] = useState(false)

    const [repoURL, setURL] = useState(auth_url_json['code'])

    console.log('passed correctly!')
    console.log(auth_url_json)

    // const sendForm = (event) => {
    //   const formData = new FormData(event.currentTarget);
    //   event.preventDefault();
    //   console.log(Array.from(formData.entries()))
    //   fetch(update_url).then(r => r.text()).then(text => {

    //     const body = { body: Array.from(formData.entries()), commit_sha : sha, user : user};
    //     const headers = { 
    //         "Content-Type": "application/json"
    //     };

    //     axios.post(text.concat("/"), body, { headers })
    //         .then(response => console.log(response));
    //   });
    // }
    const [secrets, setSecrets] = useState([])
    useEffect(() => {
      const getData = () => {
         fetch(url) // Fetch Lambda url to request from 
          .then(r => r.text()) 
          .then(async text => {
            try {
              
              // Send code + repo_url as a post request to server
              const body = {code : auth_url_json['code'], repo_url : auth_url_json['repo_url']};
              const headers = { 
                "Content-Type": "application/json"
              };

              //TODO: change url back to text.concat("/") in live
              let result = await axios.post("http://localhost:5000/report", body, headers);
              console.log(result);
              const data = (result.data)['body'];
              const token_data = (result.data)['token'];
              setSecrets(JSON.parse(data));
              setToken(token_data);
              setURL(auth_url_json['repo_url']);
              setReady(true)
            } catch (error) {
              console.log(error);
              setError(error);
            }
      });
      };
      getData();
    }, []);  


    // const [secrets, setSecrets] = useState([])
    // useEffect(() => {
    //   const getData = () => {
    //      fetch(url)
    //       .then(r => r.text()) 
    //       .then(async text => {
    //         try {
    //           let result = await axios.get(text.concat("/")); 

    //           setSecrets(result.data);
    //           console.log(result);
    //           console.log(result.data);
    //         } catch (error) {
    //           console.log(error);
    //         }
    //   });
    //   };
    //   getData();
    // }, []);  
    

    const sendForm = (event) => {
      const formData = new FormData(event.currentTarget);
      event.preventDefault();
      console.log(Array.from(formData.entries()))
      fetch(update_url).then(r => r.text()).then(text => {

        const body = { body: Array.from(formData.entries()), repo_url : repoURL, token : token};
        const headers = { 
            "Content-Type": "application/json"
        };

        axios.post(text.concat("http://localhost:5000/"), body, { headers }) //TODO: change to text.concat("/") when live
            .then(response => console.log(response));
      });
    }
    if (error === true) {
      <p>Authorization Error</p>
    } else {
      return (
        <div>
          {ready ?
          <form onSubmit={(event) => sendForm(event)}>
    
            <h2> Secrets Report</h2>
            <input type="hidden" name="id" value={repoURL}/>
    
            <p>Secrets report</p>
            
            {secrets.map(secret => (
            <div>
            <h2>{secret.id}. {secret.type} found in {secret.location}</h2>
            <a> {secret.code_location} </a>
            <ul>
                <p><input type="radio" value="hub" name={secret.id} required></input> To Hub </p>
                <p><input type="radio" value="allow" name={secret.id} required></input> To Allow </p>
            </ul>
            </div>
            ))}
    
            <p>*All boxes must be selected to send</p>
            
            <button type="submit"> Submit </button>
            </form>
            : <a>loading...</a>
            
            }
        </div>
      );
    }
}
  
  export default Report;
  