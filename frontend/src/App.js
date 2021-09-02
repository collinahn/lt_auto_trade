import React, { Component } from "react";
import { Switch, Route, Link } from "react-router-dom";
import './App.css';
import Home from './component/Home';
import Trade from './component/Trade';
import Transaction from './component/Transaction';
import Develop from './component/Develop';

class App extends Component {
  render() {
    // const { path } = this.props;
   
  return (
    <div>
    <h1 className="title">LT AUTO TRADE</h1>
    
    <div className="links">
      <Link to="/Home" className="link">Home</Link>
      <Link to="/Trade" className="link">Trade</Link>
      <Link to="/Transaction" className="link">Transaction</Link>
      <Link to="/Develop" className="link">Develop</Link>
    </div>
    <hr/>
    <div className="tabs">
      <Switch>
        <Route path="/Home" exact component={Home} />
        <Route path="/Trade" component={Trade} />
        <Route path="/Transaction" component={Transaction} />
        <Route path="/Develop" component={Develop} />
      </Switch>
      
    </div>
  </div>
);
}
}

export default App;
