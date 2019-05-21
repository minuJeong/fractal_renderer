#version 460

// specify worker size
layout(local_size_x=8, local_size_y=8) in;

layout(binding=0) buffer dst_tex
{
    vec4 out_col[];
};
layout(binding=1) buffer src_tex
{
    vec4 in_col[];
};

uniform float u_time;
uniform uint u_width;


void main()
{
    const ivec2 xy = ivec2(gl_GlobalInvocationID.xy);
    uint i = xy.x + xy.y * u_width;
    out_col[i] = in_col[i];
}
