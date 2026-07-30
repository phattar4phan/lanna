import Hero from "../components/Hero";
import Chat from "../components/Chat";
import About from "../components/About";
import Architecture from "../components/Architecture";
import LearningJourney from "../components/LearningJourney";
import ModelStats from "../components/ModelStats";
import FAQ from "../components/FAQ";
import Footer from "../components/Footer";

export default function App() {
  return (
    <main className="min-h-screen bg-[#2D2D2D]">
      <Hero />
      <Chat />
      <About />
      <Architecture />
      <LearningJourney />
      <ModelStats />
      <FAQ />
      <Footer />
    </main>
  );
}
