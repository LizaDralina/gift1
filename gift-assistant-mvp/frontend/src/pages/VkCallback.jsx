import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";

export default function VkCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState("Обработка авторизации VK...");
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const vkError = searchParams.get("error");
      const vkErrorDescription = searchParams.get("error_description");

      if (vkError) {
        setError(`VK error: ${vkErrorDescription || vkError}`);
        return;
      }

      if (!code || !state) {
        setError("Не получены code или state от VK");
        return;
      }

      try {
        const result = await api.exchangeVkCode({ code, state });
        setStatus(
          `Импорт завершён. Добавлено интересов: ${result.imported_interests?.join(", ") || "0"}`
        );

        setTimeout(() => {
          navigate("/dashboard");
        }, 1500);
      } catch (err) {
        setError(err.message);
      }
    };

    run();
  }, [searchParams, navigate]);

  return (
    <div className="card">
      <h1>Импорт интересов из VK</h1>
      {error ? <div className="error">{error}</div> : <p>{status}</p>}
    </div>
  );
}