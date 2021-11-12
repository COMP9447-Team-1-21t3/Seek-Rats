import logo from '../logo.svg';
import '../App.css';
import React, { useEffect, useState } from "react";
import url from './config.txt';
import update_url from './config2.txt';
import axios from "axios";

function Report() {

    // const [secrets, setSecrets] = useState([{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
    // {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}])
    const [secrets, setSecrets] = useState([])
    const [user, setUser] = useState("9999999")
    
    const commit_id = "asdasd"
    const sha = "Asdasda"
    const date = "asdasd"
    

    useEffect(() => {
      const getData = () => {
         fetch(url)
          .then(r => r.text()) 
          .then(async text => {
            try {
              let result = await axios.get(text.concat("/"));

              setSecrets(result.data);
              console.log(result);
              console.log(result.data);
            } catch (error) {
              console.log(error);
            }
      });
      };
      getData();
    }, []);  
    

    const sendForm = (event) => {
      const formData = new FormData(event.currentTarget);
      event.preventDefault();
      console.log(Array.from(formData.entries()))
      fetch(update_url).then(r => r.text()).then(text => {

        const body = { body: Array.from(formData.entries()), commit_sha : sha, user : user};
        const headers = { 
            "Content-Type": "application/json"
        };

        axios.post(text.concat("/"), body, { headers })
            .then(response => console.log(response));
      });
    }

    return (
      <div>

        <form onSubmit={(event) => sendForm(event)}>
  
          <h2> Secrets Report</h2>
          <input type="hidden" name="id" value={commit_id}/>
          <input type="hidden" name="sha" value={sha}/>
  
          
          <p>Secrets report {date}</p>
  
          {secrets.map(secret => (
          <div>
          <h2>{secret.id} {secret.type} found in {secret.location}</h2>
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
        
      </div>
    );
  }
  
  export default Report;
  