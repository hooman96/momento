import React, { useState, useEffect } from "react";
import cn from "classnames";
import styles from "./LLMPlayground.module.sass";

const API_BASE = "http://localhost:8005";

const LLMPlayground = () => {
  const [models, setModels] = useState([]);
  const [displayNames, setDisplayNames] = useState({});
  const [selectedModels, setSelectedModels] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedRow, setExpandedRow] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/models`)
      .then((res) => res.json())
      .then((data) => {
        setModels(data.default_model_ids || []);
        setDisplayNames(data.display_names || {});
        setSelectedModels(data.default_model_ids || []);
      })
      .catch(() =>
        setError("Could not connect to the backend at " + API_BASE)
      );
  }, []);

  const toggleModel = (modelId) => {
    setSelectedModels((prev) =>
      prev.includes(modelId)
        ? prev.filter((m) => m !== modelId)
        : [...prev, modelId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    if (selectedModels.length === 0) {
      setError("Select at least one model.");
      return;
    }

    setLoading(true);
    setError("");
    setResponses({});
    setExpandedRow(null);

    try {
      const body = {
        prompt: prompt.trim(),
        model_ids: selectedModels,
      };
      if (showSystemPrompt && systemPrompt.trim()) {
        body.system_prompt = systemPrompt.trim();
      }

      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setResponses(data.responses || {});
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const getShortName = (modelId) => {
    return (
      displayNames[modelId] || modelId.split("/").pop().replace(":free", "")
    );
  };

  const truncate = (text, len = 120) => {
    if (!text || text.length <= len) return text;
    return text.slice(0, len) + "…";
  };

  const hasResults = Object.keys(responses).length > 0;

  return (
    <div className={styles.section}>
      <div className={cn("container", styles.container)}>


        <div className={styles.layout}>
          {/* ── LEFT PANEL: Input ── */}
          <div className={styles.left}>
            <form className={styles.form} onSubmit={handleSubmit}>
              <div className={styles.models}>
                <div className={styles.modelsLabel}>Models</div>
                <div className={styles.modelsList}>
                  {models.map((m) => (
                    <label key={m} className={styles.modelChip}>
                      <input
                        type="checkbox"
                        checked={selectedModels.includes(m)}
                        onChange={() => toggleModel(m)}
                      />
                      <span
                        className={cn(styles.chipInner, {
                          [styles.chipActive]: selectedModels.includes(m),
                        })}
                      >
                        {getShortName(m)}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <button
                type="button"
                className={styles.toggleSystem}
                onClick={() => setShowSystemPrompt(!showSystemPrompt)}
              >
                {showSystemPrompt ? "− Hide" : "+ Add"} System Prompt
              </button>

              {showSystemPrompt && (
                <textarea
                  className={styles.textarea}
                  rows={3}
                  placeholder="System prompt (optional)"
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                />
              )}

              <textarea
                className={cn(styles.textarea, styles.mainInput)}
                rows={6}
                placeholder="Enter your prompt here…"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />

              {error && <div className={styles.error}>{error}</div>}

              <button
                type="submit"
                className={cn("button", styles.submit)}
                disabled={loading || !prompt.trim()}
              >
                {loading ? "Generating…" : "Send to Models"}
              </button>
            </form>
          </div>

          {/* ── RIGHT PANEL: Results ── */}
          <div className={styles.right}>
            <div className={styles.resultsHeader}>
              <div className={styles.resultsTitle}>Responses</div>
              {hasResults && (
                <div className={styles.resultsBadge}>
                  {Object.keys(responses).length} model
                  {Object.keys(responses).length > 1 ? "s" : ""}
                </div>
              )}
            </div>

            {loading && (
              <div className={styles.loader}>
                <div className={styles.spinner} />
                <span>
                  Querying {selectedModels.length} model
                  {selectedModels.length > 1 ? "s" : ""}…
                </span>
              </div>
            )}

            {!loading && !hasResults && (
              <div className={styles.empty}>
                Results will appear here after you send a prompt.
              </div>
            )}

            {hasResults && (
              <div className={styles.tableWrap}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th className={styles.thModel}>Model</th>
                      <th className={styles.thResponse}>Response</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(responses).map(([modelId, text]) => {
                      const isExpanded = expandedRow === modelId;
                      return (
                        <React.Fragment key={modelId}>
                          <tr
                            className={cn(styles.row, {
                              [styles.rowExpanded]: isExpanded,
                            })}
                            onClick={() =>
                              setExpandedRow(isExpanded ? null : modelId)
                            }
                          >
                            <td className={styles.tdModel}>
                              <span className={styles.modelBadge}>
                                {getShortName(modelId)}
                              </span>
                            </td>
                            <td className={styles.tdResponse}>
                              {isExpanded ? (
                                <pre className={styles.fullText}>{text}</pre>
                              ) : (
                                <span className={styles.preview}>
                                  {truncate(text)}
                                </span>
                              )}
                            </td>
                          </tr>
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMPlayground;
