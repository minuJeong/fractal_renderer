#version 460

uniform mat4 MVP;

in vec3 in_pos;

out vec2 v_uv;

void main()
{
    v_uv = in_pos.xy;
    gl_Position = vec4(in_pos, 1.0);
}
