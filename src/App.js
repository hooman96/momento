import React from 'react';
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import "./styles/app.sass";
import Page from "./components/Page";
import Home from "./screens/Home";
import Download from "./screens/Download";
import Class01 from "./screens/Class01";
import Class02 from "./screens/Class02";
import Class02Details from "./screens/Class02Details";
import Lifestyle from "./screens/Lifestyle";
import ReactGA from "react-ga";

export const initGA = () => {
  ReactGA.initialize("G-HETBFN8JGK");
};

const routes = [
  { path: '/',                component: Home         },
  { path: '/download',        component: Download     },
  { path: '/class01',         component: Class01      },
  { path: '/class02',         component: Class02      },
  { path: '/class02-details', component: Class02Details },
  { path: '/lifestyle',       component: Lifestyle    },
];

function App() {
  return (
    <Router>
      <Switch>
        {routes.map(({ path, component: Screen }) => (
          <Route
            key={path}
            exact
            path={path}
            render={() => (
              <Page>
                <Screen />
              </Page>
            )}
          />
        ))}
      </Switch>
    </Router>
  );
}

export default App;