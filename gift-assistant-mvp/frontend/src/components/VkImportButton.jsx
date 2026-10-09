import { useEffect, useRef } from "react";
import { api } from "../api/client";

export default function VkImportButton({ recipientId, onSuccess }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://unpkg.com/@vkid/sdk@<3.0.0/dist-sdk/umd/index.js";
    script.async = true;

    script.onload = () => {
      if (!window.VKIDSDK || !containerRef.current) return;

      const VKID = window.VKIDSDK;

      VKID.Config.init({
        app: 54484643,
        redirectUrl: "https://inspective-imperishably-sau.ngrok-free.dev/vk/callback",
        responseMode: VKID.ConfigResponseMode.Callback,
        source: VKID.ConfigSource.LOWCODE,
        scope: "groups",
      });

      const oneTap = new VKID.OneTap();

      oneTap
        .render({
          container: containerRef.current,
          showAlternativeLogin: true
        })
        .on(VKID.WidgetEvents.ERROR, (error) => {
          console.error("VKID error:", error);
          alert("Ошибка VK авторизации");
        })
        .on(VKID.OneTapInternalEvents.LOGIN_SUCCESS, async (payload) => {
          try {
            const code = payload.code;
            const deviceId = payload.device_id;

            const data = await VKID.Auth.exchangeCode(code, deviceId);

            const accessToken =
              data?.access_token ||
              data?.tokens?.access_token ||
              data?.token;

            if (!accessToken) {
              throw new Error("Не удалось получить access_token из VK");
            }

            const result = await api.importVkToken({
              recipient_id: recipientId,
              access_token: accessToken
            });

            alert("Интересы импортированы из VK");
            if (onSuccess) onSuccess(result);
          } catch (err) {
            console.error(err);
            alert(err.message || "Ошибка импорта из VK");
          }
        });
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [recipientId, onSuccess]);

  return <div ref={containerRef}></div>;
}