import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import InteractiveActions from "@/components/InteractiveActions";
import CompareSimulator from "@/components/CompareSimulator";
import DoctorDemo from "@/components/DoctorDemo";
import QuickStart from "@/components/QuickStart";
import Footer from "@/components/Footer";

export default function HomePage() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Features />
        <InteractiveActions />
        <CompareSimulator />
        <DoctorDemo />
        <QuickStart />
      </main>
      <Footer />
    </>
  );
}
