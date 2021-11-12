import logo from './logo.svg';
import './App.css';
import React, { useEffect, useState } from "react";
import Report from './components/Report';
import Auth from './components/Auth';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

function App() {

  return (
  <Router>
    <Switch>
      <Route path="/report" component={Report}/>
    </Switch>
    <Switch>
      <Route path="/" component={Auth}/>
    </Switch>
  </Router>
  )
}

export default App;
