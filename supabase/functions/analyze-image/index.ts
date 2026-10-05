// Cloud inference is deliberately disabled. Never forward camera frames to a provider.
Deno.serve((_request: Request) => new Response(JSON.stringify({
  error: "CLOUD_INFERENCE_DISABLED",
  message: "Use the local CivicEye ONNX /detect endpoint."
}), { status: 410, headers: {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*"
}}));
