import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { storyData } from "./storyData";

export default function App() {
  const [sceneId, setSceneId] = useState("intro");
  const [score, setScore] = useState(0);
  const [result, setResult] = useState("");

  const scene = useMemo(
    () => storyData.find((item) => item.id === sceneId),
    [sceneId]
  );

  function goNext(nextId) {
    setResult("");
    setSceneId(nextId);
  }

  function choose(choice) {
    setResult(choice.result);
    setScore((prev) => prev + choice.score);

    setTimeout(() => {
      setResult("");
      setSceneId(choice.next);
    }, 2600);
  }

  function restart() {
    setSceneId("intro");
    setScore(0);
    setResult("");
  }

  return (
    <main className="experience">
      <div className="grain" />
      <div className="vignette" />

      <AnimatePresence mode="wait">
        <motion.section
          key={scene.id}
          className="scene-card"
          initial={{ opacity: 0, y: 18, filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -18, filter: "blur(8px)" }}
          transition={{ duration: 0.7 }}
        >
          <p className="eyebrow">{scene.eyebrow}</p>
          <h1>{scene.title}</h1>

          <div className="story-text">
            {scene.text?.map((line, index) => (
              <motion.p
                key={index}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 + index * 0.25 }}
              >
                {line}
              </motion.p>
            ))}
          </div>

          {scene.type === "intro" && (
            <button className="primary-btn" onClick={() => goNext(scene.next)}>
              {scene.button}
            </button>
          )}

          {scene.choices && !result && (
            <div className="choices">
              {scene.choices.map((choice) => (
                <button key={choice.label} onClick={() => choose(choice)}>
                  {choice.label}
                </button>
              ))}
            </div>
          )}

          {result && (
            <motion.div
              className="result-box"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              {result}
            </motion.div>
          )}

          {scene.type === "final" && (
            <div className="final">
              <blockquote>{scene.quote}</blockquote>
              <p className="score">Millî İrade Puanı: {score}/8</p>
              <button className="primary-btn" onClick={restart}>
                Yeniden Başla
              </button>
            </div>
          )}
        </motion.section>
      </AnimatePresence>
    </main>
  );
}
