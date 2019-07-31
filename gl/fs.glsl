#version 460

layout(binding=0) buffer u_texture_0
{
    vec4 tex_col[];
};

uniform int u_width;
uniform int u_height;

in vec2 v_uv;
out vec4 out_col;

void main()
{
    vec2 uv = v_uv * 0.5 + 0.5;
    uv.x += 0.5;
    vec2 wh = vec2(u_width, u_height);
    vec2 xy = uv * wh;
    float p = xy.x + xy.y * u_width;
    int i = int(p);

    vec3 col = tex_col[i].xyz;
    out_col = vec4(col, 1.0);
}
