import 'bootstrap-icons/font/bootstrap-icons.css';
import Button from './Button';

import paytonImg from '../assets/payton.png';
import kushImg from '../assets/kush.png';
import lillianImg from '../assets/lillian.png';
import natashaImg from '../assets/natasha.png';
import samImg from '../assets/sam.png';
import sarahImg from '../assets/sarah.png';

interface AboutProps {
  onBack: () => void;
}

interface TeamMember {
  name: string;
  email: string;
  photo: string;
  linkedin: string;
  graduation: string;
}

const TEAM: TeamMember[] = [
  {
    name: 'Kush Patel',
    email: 'patelkush@oregonstate.edu',
    photo: kushImg,
    linkedin: 'https://www.linkedin.com/in/kushp839/',
    graduation: 'Graduating June 2026',
  },
  {
    name: 'Sarah Satchell',
    email: 'satchels@oregonstate.edu',
    photo: sarahImg,
    linkedin: 'https://www.linkedin.com/in/sarahsatchell/',
    graduation: 'Graduating June 2026',
  },
  {
    name: 'Lilian Le',
    email: 'lelili@oregonstate.edu',
    photo: lillianImg,
    linkedin: 'https://www.linkedin.com/in/lilian-le-01b576254/',
    graduation: 'Graduating June 2026',
  },
  {
    name: 'Payton Brafield',
    email: 'bradfiep@oregonstate.edu',
    photo: paytonImg,
    linkedin: 'https://www.linkedin.com/in/paytonbradfield/',
    graduation: 'Graduating June 2026',
  },
  {
    name: 'Natalia Zaitseva',
    email: 'zaitsevn@oregonstate.edu',
    photo: natashaImg,
    linkedin: 'https://www.linkedin.com/in/natalia-zaitseva-78153a252/',
    graduation: 'Graduating June 2026',
  },
  {
    name: 'Samuel Garcia-Lopez',
    email: 'garcsamu@oregonstate.edu',
    photo: samImg,
    linkedin: 'https://www.linkedin.com/in/sam-garcia-lopez-5640392b2/',
    graduation: 'Graduating June 2026',
  },
];

interface Feature {
  icon: string;
  title: string;
  body: string;
}

const FEATURES: Feature[] = [
  {
    icon: 'bi-cpu',
    title: 'Self-Organizing Agents',
    body: 'Independent agents explore the maze, share discoveries, and converge on the shortest path without central coordination.',
  },
  {
    icon: 'bi-broadcast',
    title: 'Real-Time Streaming',
    body: 'A WebSocket bridge streams every step, message, and decision from the Python backend to the React UI as it happens.',
  },
  {
    icon: 'bi-grid-3x3',
    title: 'Build or Import Mazes',
    body: 'Design mazes in the browser, paste raw grids, or load CSV files — then watch the agents take on whatever you throw at them.',
  },
  {
    icon: 'bi-bar-chart',
    title: 'Per-Agent Analytics',
    body: 'Inspect steps taken, cells visited, and frontiers explored for each agent in a live stats popup as the run progresses.',
  },
];

interface TechItem {
  icon: string;
  label: string;
}

const TECH: TechItem[] = [
  { icon: 'bi-filetype-tsx', label: 'React + TypeScript' },
  { icon: 'bi-lightning-charge', label: 'Vite' },
  { icon: 'bi-filetype-py', label: 'Python' },
  { icon: 'bi-arrow-left-right', label: 'WebSockets' },
  { icon: 'bi-check2-square', label: 'Vitest' },
  { icon: 'bi-bootstrap', label: 'Bootstrap Icons' },
];

interface Step {
  number: string;
  title: string;
  body: string;
}

const STEPS: Step[] = [
  {
    number: '01',
    title: 'Define the Maze',
    body: 'Build a grid in the editor or import one from CSV, then mark start and end points.',
  },
  {
    number: '02',
    title: 'Deploy the Agents',
    body: 'Multiple agents are spawned and begin exploring the maze in parallel from the start cell.',
  },
  {
    number: '03',
    title: 'Coordinate at the Edge',
    body: 'Agents broadcast their findings — visited cells, dead ends, and promising frontiers — over WebSockets.',
  },
  {
    number: '04',
    title: 'Converge on a Path',
    body: 'The collective merges discoveries into the fastest route from start to end, faster than any single explorer could.',
  },
];

export default function About({ onBack }: AboutProps) {
  return (
    <div className="about-section">
      <div className="about-section-inner">
        <h1 className="about-title">About the Project</h1>

        <section className="about-card about-overview">
          <h2 className="about-subtitle">
            <i className="bi bi-compass about-subtitle-icon" aria-hidden="true"></i>
            Project Overview
          </h2>
          <p className="about-paragraph">
            Multi-Agent Maze Solver is a collaborative pathfinding simulation
            where AI agents explore mazes and communicate to find the fastest
            route from a start point to an end point. Built as part of CS 467
            at Oregon State University, this project explores how
            self-organizing agents can coordinate at the edge to solve spatial
            problems more efficiently than any single agent could on its own.
          </p>
          <p className="about-paragraph">
            The system pairs a React + TypeScript frontend with a Python
            backend that streams agent activity over WebSockets. Users can
            build or import mazes, watch agents navigate them in real time, and
            inspect per-agent statistics as they go.
          </p>
        </section>

        <section className="about-card about-features">
          <h2 className="about-subtitle">
            <i className="bi bi-stars about-subtitle-icon" aria-hidden="true"></i>
            Key Features
          </h2>
          <div className="features-grid">
            {FEATURES.map((feature) => (
              <div className="feature-tile" key={feature.title}>
                <div className="feature-icon-wrap">
                  <i className={`bi ${feature.icon}`} aria-hidden="true"></i>
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-body">{feature.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="about-card about-how">
          <h2 className="about-subtitle">
            <i className="bi bi-diagram-3 about-subtitle-icon" aria-hidden="true"></i>
            How It Works
          </h2>
          <ol className="steps-list">
            {STEPS.map((step) => (
              <li className="step-item" key={step.number}>
                <span className="step-number">{step.number}</span>
                <div className="step-text">
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-body">{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="about-card about-tech">
          <h2 className="about-subtitle">
            <i className="bi bi-stack about-subtitle-icon" aria-hidden="true"></i>
            Tech Stack
          </h2>
          <ul className="tech-chip-list">
            {TECH.map((item) => (
              <li className="tech-chip" key={item.label}>
                <i className={`bi ${item.icon}`} aria-hidden="true"></i>
                <span>{item.label}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="about-card about-team">
          <h2 className="about-subtitle">
            <i className="bi bi-people-fill about-subtitle-icon" aria-hidden="true"></i>
            About the Team
          </h2>
          <div className="team-grid">
            {TEAM.map((member) => (
              <article className="team-card" key={member.email}>
                <img
                  className="team-photo"
                  src={member.photo}
                  alt={`Headshot of ${member.name}`}
                />
                <h3 className="team-card-name">{member.name}</h3>
                <p className="team-card-grad">
                  <i className="bi bi-mortarboard-fill" aria-hidden="true"></i>
                  {member.graduation}
                </p>
                <a
                  className="team-card-link"
                  href={`mailto:${member.email}`}
                >
                  <i className="bi bi-envelope-fill" aria-hidden="true"></i>
                  <span>{member.email}</span>
                </a>
                <a
                  className="team-card-link team-card-linkedin"
                  href={member.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i className="bi bi-linkedin" aria-hidden="true"></i>
                  <span>LinkedIn</span>
                </a>
              </article>
            ))}
          </div>
        </section>

        <section className="about-card about-ack">
          <h2 className="about-subtitle">
            <i className="bi bi-award about-subtitle-icon" aria-hidden="true"></i>
            Acknowledgements
          </h2>
          <p className="about-paragraph">
            This project was developed as a Senior Capstone (CS 467) at Oregon
            State University. We thank our instructors and project sponsor for
            their guidance, and the open-source community whose tools and
            libraries made this work possible.
          </p>
        </section>

        <div className="about-actions">
          <Button onClick={onBack}>Back to Home</Button>
        </div>
      </div>
    </div>
  );
}
