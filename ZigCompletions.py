import sublime
import sublime_plugin
import re
import os
import platform
import glob
import fnmatch
import time


class ZigCompletions(sublime_plugin.EventListener):
  built_in_procs = [
    ['@addWithOverflow(comptime T: type, a: T, b: T, result: *T) bool 	Built-in', 'addWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})'],
    ['@alignCast(comptime alignment: u29, ptr: var) var 	Built-in', 'alignCast(${1:comptime alignment: u29}, ${2:ptr: var})'],
    ['@alignOf(comptime T: type) comptime_int 	Built-in', 'alignOf(${1:comptime T: type})'],
    ['@as(comptime T: type, expression) T 	Built-in', 'as(${1:comptime T: type}, ${2:expression})'],
    ['@asyncCall(frame_buffer: []align(@alignOf(@Frame(anyAsyncFunction))) u8, result_ptr, function_ptr, args: ...) anyframe->T 	Built-in', 'asyncCall(${1:frame_buffer: []align(@alignOf(@Frame(anyAsyncFunction))) u8}, ${2:result_ptr}, ${3:function_ptr}, ${4:args: ...})'],
    ['@atomicLoad(comptime T: type, ptr: *const T, comptime ordering: builtin.AtomicOrder) T 	Built-in', 'atomicLoad(${1:comptime T: type}, ${2:ptr: *const T}, ${3:comptime ordering: builtin.AtomicOrder})'],
    ['@atomicRmw(comptime T: type, ptr: *T, comptime op: builtin.AtomicRmwOp, operand: T, comptime ordering: builtin.AtomicOrder) T 	Built-in', 'atomicRmw(${1:comptime T: type}, ${2:ptr: *T}, ${3:comptime op: builtin.AtomicRmwOp}, ${4:operand: T}, ${5:comptime ordering: builtin.AtomicOrder})'],
    ['@atomicStore(comptime T: type, ptr: *T, value: T, comptime ordering: builtin.AtomicOrder) void 	Built-in', 'atomicStore(${1:comptime T: type}, ${2:ptr: *T}, ${3:value: T}, ${4:comptime ordering: builtin.AtomicOrder})'],
    ['@bitCast(comptime DestType: type, value: var) DestType 	Built-in', 'bitCast(${1:comptime DestType: type}, ${2:value: var})'],
    ['@bitOffsetOf(comptime T: type, comptime field_name: []const u8) comptime_int 	Built-in', 'bitOffsetOf(${1:comptime T: type}, ${2:comptime field_name: []const u8})'],
    ['@boolToInt(value: bool) u1 	Built-in', 'boolToInt(${1:value: bool})'],
    ['@bitSizeOf(comptime T: type) comptime_int 	Built-in', 'bitSizeOf(${1:comptime T: type})'],
    ['@breakpoint() 	Built-in', 'breakpoint()'],
    ['@mulAdd(comptime T: type, a: T, b: T, c: T) T 	Built-in', 'mulAdd(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:c: T})'],
    ['@byteSwap(comptime T: type, operand: T) T 	Built-in', 'byteSwap(${1:comptime T: type}, ${2:operand: T})'],
    ['@bitReverse(comptime T: type, integer: T) T 	Built-in', 'bitReverse(${1:comptime T: type}, ${2:integer: T})'],
    ['@byteOffsetOf(comptime T: type, comptime field_name: []const u8) comptime_int 	Built-in', 'byteOffsetOf(${1:comptime T: type}, ${2:comptime field_name: []const u8})'],
    ['@call(options: std.builtin.CallOptions, function: var, args: var) var 	Built-in', 'call(${1:options: std.builtin.CallOptions}, ${2:function: var}, ${3:args: var})'],
    ['@cDefine(comptime name: []u8, value) 	Built-in', 'cDefine(${1:comptime name: []u8}, ${2:value})'],
    ['@cImport(expression) type 	Built-in', 'cImport(${1:expression})'],
    ['@cInclude(comptime path: []u8) 	Built-in', 'cInclude(${1:comptime path: []u8})'],
    ['@clz(comptime T: type, integer: T) 	Built-in', 'clz(${1:comptime T: type}, ${2:integer: T})'],
    ['@cmpxchgStrong(comptime T: type, ptr: *T, expected_value: T, new_value: T, success_order: AtomicOrder, fail_order: AtomicOrder) ?T 	Built-in', 'cmpxchgStrong(${1:comptime T: type}, ${2:ptr: *T}, ${3:expected_value: T}, ${4:new_value: T}, ${5:success_order: AtomicOrder}, ${6:fail_order: AtomicOrder})'],
    ['@cmpxchgWeak(comptime T: type, ptr: *T, expected_value: T, new_value: T, success_order: AtomicOrder, fail_order: AtomicOrder) ?T 	Built-in', 'cmpxchgWeak(${1:comptime T: type}, ${2:ptr: *T}, ${3:expected_value: T}, ${4:new_value: T}, ${5:success_order: AtomicOrder}, ${6:fail_order: AtomicOrder})'],
    ['@compileError(comptime msg: []u8) 	Built-in', 'compileError(${1:comptime msg: []u8})'],
    ['@compileLog(args: ...) 	Built-in', 'compileLog(${1:args: ...})'],
    ['@ctz(comptime T: type, integer: T) 	Built-in', 'ctz(${1:comptime T: type}, ${2:integer: T})'],
    ['@cUndef(comptime name: []u8) 	Built-in', 'cUndef(${1:comptime name: []u8})'],
    ['@divExact(numerator: T, denominator: T) T 	Built-in', 'divExact(${1:numerator: T}, ${2:denominator: T})'],
    ['@divFloor(numerator: T, denominator: T) T 	Built-in', 'divFloor(${1:numerator: T}, ${2:denominator: T})'],
    ['@divTrunc(numerator: T, denominator: T) T 	Built-in', 'divTrunc(${1:numerator: T}, ${2:denominator: T})'],
    ['@embedFile(comptime path: []const u8) *const [X:0]u8 	Built-in', 'embedFile(${1:comptime path: []const u8})'],
    ['@enumToInt(enum_or_tagged_union: var) var 	Built-in', 'enumToInt(${1:enum_or_tagged_union: var})'],
    ['@errorName(err: anyerror) []const u8 	Built-in', 'errorName(${1:err: anyerror})'],
    ['@errorReturnTrace() ?*builtin.StackTrace 	Built-in', 'errorReturnTrace()'],
    ['@errorToInt(err: var) std.meta.IntType(false, @sizeOf(anyerror) * 8) 	Built-in', 'errorToInt(${1:err: var) std.meta.IntType(false}, ${2:@sizeOf(anyerror})'],
    ['@errSetCast(comptime T: DestType, value: var) DestType 	Built-in', 'errSetCast(${1:comptime T: DestType}, ${2:value: var})'],
    ['@export(target: var, comptime options: std.builtin.ExportOptions) void 	Built-in', 'export(${1:target: var}, ${2:comptime options: std.builtin.ExportOptions})'],
    ['@fence(order: AtomicOrder) 	Built-in', 'fence(${1:order: AtomicOrder})'],
    ['@field(lhs: var, comptime field_name: []const u8) (field) 	Built-in', 'field(${1:lhs: var}, ${2:comptime field_name: []const u8})'],
    ['@fieldParentPtr(comptime ParentType: type, comptime field_name: []const u8, field_ptr: *T) *ParentType 	Built-in', 'fieldParentPtr(${1:comptime ParentType: type}, ${2:comptime field_name: []const u8}, ${3: field_ptr: *T})'],
    ['@floatCast(comptime DestType: type, value: var) DestType 	Built-in', 'floatCast(${1:comptime DestType: type}, ${2:value: var})'],
    ['@floatToInt(comptime DestType: type, float: var) DestType 	Built-in', 'floatToInt(${1:comptime DestType: type}, ${2:float: var})'],
    ['@frame() *@Frame(func) 	Built-in', 'frame()'],
    ['@Frame(func: var) type 	Built-in', 'Frame(${1:func: var})'],
    ['@frameAddress() usize 	Built-in', 'frameAddress()'],
    ['@frameSize() usize 	Built-in', 'frameSize()'],
    ['@hasDecl(comptime Container: type, comptime name: []const u8) bool 	Built-in', 'hasDecl(${1:comptime Container: type}, ${2:comptime name: []const u8})'],
    ['@hasField(comptime Container: type, comptime name: []const u8) bool 	Built-in', 'hasField(${1:comptime Container: type}, ${2:comptime name: []const u8})'],
    ['@import(comptime path: []u8) type 	Built-in', 'import(${1:comptime path: []u8})'],
    ['@intCast(comptime DestType: type, int: var) DestType 	Built-in', 'intCast(${1:comptime DestType: type}, ${2:int: var})'],
    ['@intToEnum(comptime DestType: type, int_value: @TagType(DestType)) DestType 	Built-in', 'intToEnum(${1:comptime DestType: type}, ${2:int_value: @TagType(DestType)})'],
    ['@intToError(value: std.meta.IntType(false, @sizeOf(anyerror) * 8)) anyerror 	Built-in', 'intToError(${1:value: std.meta.IntType(false, @sizeOf(anyerror) * 8)})'],
    ['@intToFloat(comptime DestType: type, int: var) DestType 	Built-in', 'intToFloat(${1:comptime DestType: type}, ${2:int: var})'],
    ['@intToPtr(comptime DestType: type, address: usize) DestType 	Built-in', 'intToPtr(${1:comptime DestType: type}, ${2:address: usize})'],
    ['@memcpy(noalias dest: [*]u8, noalias source: [*]const u8, byte_count: usize) 	Built-in', 'memcpy(${1:noalias dest: [*]u8}, ${2:noalias source: [*]const u8}, ${3:byte_count: usize})'],
    ['@memset(dest: [*]u8, c: u8, byte_count: usize) 	Built-in', 'memset(${1:dest: [*]u8}, ${2:c: u8}, ${3:byte_count: usize})'],
    ['@mod(numerator: T, denominator: T) T 	Built-in', 'mod(${1:numerator: T}, ${2:denominator: T})'],
    ['@mulWithOverflow(comptime T: type, a: T, b: T, result: *T) bool 	Built-in', 'mulWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})'],
    ['@OpaqueType() type 	Built-in', 'OpaqueType()'],
    ['@panic(message: []const u8) noreturn 	Built-in', 'panic(${1:message: []const u8})'],
    ['@popCount(comptime T: type, integer: T) 	Built-in', 'popCount(${1:comptime T: type}, ${2:integer: T})'],
    ['@ptrCast(comptime DestType: type, value: var) DestType 	Built-in', 'ptrCast(${1:comptime DestType: type}, ${2:value: var})'],
    ['@ptrToInt(value: var) usize 	Built-in', 'ptrToInt(${1:value: var})'],
    ['@rem(numerator: T, denominator: T) T 	Built-in', 'rem(${1:numerator: T}, ${2:denominator: T})'],
    ['@returnAddress() usize 	Built-in', 'returnAddress()'],
    ['@setAlignStack(comptime alignment: u29) 	Built-in', 'setAlignStack(${1:comptime alignment: u29})'],
    ['@setCold(is_cold: bool) 	Built-in', 'setCold(${1:is_cold: bool})'],
    ['@setEvalBranchQuota(new_quota: usize) 	Built-in', 'setEvalBranchQuota(${1:new_quota: usize})'],
    ['@setFloatMode(mode: @import("builtin").FloatMode) 	Built-in', 'setFloatMode(${1:mode: @import("builtin").FloatMode})'],
    ['@setRuntimeSafety(safety_on: bool) 	Built-in', 'setRuntimeSafety(${1:safety_on: bool})'],
    ['@shlExact(value: T, shift_amt: Log2T) T 	Built-in', 'shlExact(${1:value: T}, ${2:shift_amt: Log2T})'],
    ['@shlWithOverflow(comptime T: type, a: T, shift_amt: Log2T, result: *T) bool 	Built-in', 'shlWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:shift_amt: Log2T}, ${4:result: *T})'],
    ['@shrExact(value: T, shift_amt: Log2T) T 	Built-in', 'shrExact(${1:value: T}, ${2:shift_amt: Log2T})'],
    ['@shuffle(comptime E: type, a: @Vector(a_len, E), b: @Vector(b_len, E), comptime mask: @Vector(mask_len, i32)) @Vector(mask_len, E) 	Built-in', 'shuffle(${1:comptime E: type}, ${2:a: @Vector(a_len, E)}, ${3:b: @Vector(b_len, E)}, ${4:comptime mask: @Vector(mask_len, i32)})'],
    ['@sizeOf(comptime T: type) comptime_int 	Built-in', 'sizeOf(${1:comptime T: type})'],
    ['@splat(comptime len: u32, scalar: var) @Vector(len, @TypeOf(scalar)) 	Built-in', 'splat(${1:comptime len: u32}, ${2:scalar: var})'],
    ['@sqrt(value: var) @TypeOf(value) 	Built-in', 'sqrt(${1:value: var})'],
    ['@sin(value: var) @TypeOf(value) 	Built-in', 'sin(${1:value: var})'],
    ['@cos(value: var) @TypeOf(value) 	Built-in', 'cos(${1:value: var})'],
    ['@exp(value: var) @TypeOf(value) 	Built-in', 'exp(${1:value: var})'],
    ['@exp2(value: var) @TypeOf(value) 	Built-in', 'exp2(${1:value: var})'],
    ['@log(value: var) @TypeOf(value) 	Built-in', 'log(${1:value: var})'],
    ['@log2(value: var) @TypeOf(value) 	Built-in', 'log2(${1:value: var})'],
    ['@log10(value: var) @TypeOf(value) 	Built-in', 'log10(${1:value: var})'],
    ['@fabs(value: var) @TypeOf(value) 	Built-in', 'fabs(${1:value: var})'],
    ['@floor(value: var) @TypeOf(value) 	Built-in', 'floor(${1:value: var})'],
    ['@ceil(value: var) @TypeOf(value) 	Built-in', 'ceil(${1:value: var})'],
    ['@trunc(value: var) @TypeOf(value) 	Built-in', 'trunc(${1:value: var})'],
    ['@round(value: var) @TypeOf(value) 	Built-in', 'round(${1:value: var})'],
    ['@subWithOverflow(comptime T: type, a: T, b: T, result: *T) bool 	Built-in', 'subWithOverflow(${1:comptime T: type}, ${2:a: T}, ${3:b: T}, ${4:result: *T})'],
    ['@tagName(value: var) []const u8 	Built-in', 'tagName(${1:value: var})'],
    ['@TagType(T: type) type 	Built-in', 'TagType(${1:T: type})'],
    ['@This() type 	Built-in', 'This()'],
    ['@truncate(comptime T: type, integer: var) T 	Built-in', 'truncate(${1:comptime T: type}, ${2:integer: var})'],
    ['@Type(comptime info: @import("builtin").TypeInfo) type 	Built-in', 'Type(${1:comptime info: @import("builtin").TypeInfo})'],
    ['@typeInfo(comptime T: type) @import("std").builtin.TypeInfo 	Built-in', 'typeInfo(${1:comptime T: type})'],
    ['@typeName(T: type) [N]u8 	Built-in', 'typeName(${1:T: type})'],
    ['@TypeOf(...) type 	Built-in', 'TypeOf(${1:...})'],
    ['@unionInit(comptime Union: type, comptime active_field_name: []const u8, init_expr) Union 	Built-in', 'unionInit(${1:comptime Union: type}, ${2:comptime active_field_name: []const u8}, ${3:init_expr})'],
    ['@Vector(comptime len: u32, comptime ElemType: type) type 	Built-in', 'Vector(${1:comptime len: u32}, ${2:comptime ElemType: type})'],
  ]

  # return True if all the previous chars are valid (a-zA-Z0-9_) up to the '.'
  def get_prefix_before_dot(self, file_view, loc):
    # next char should be some type of space, paren or non-word
    next_char = file_view.substr(sublime.Region(loc, loc + 1))
    if next_char.isalnum():
      return False

    # walk backwards until we find a '.'. If we hit a non-char (a-zA-Z0-9_) bail out since this isnt a completion
    curr_line_region = file_view.line(loc)

    def get_before_dot(dot_loc):
      region_end = dot_loc
      while dot_loc > curr_line_region.begin():
        prev_char = file_view.substr(sublime.Region(dot_loc - 1, dot_loc))
        if prev_char.isalnum() or prev_char == '_':
          dot_loc -= 1
        else:
          return file_view.substr(sublime.Region(dot_loc, region_end))
      return None

    while loc > curr_line_region.begin():
      char = file_view.substr(sublime.Region(loc - 1, loc))
      if char == '.':
        return get_before_dot(loc - 1)

      if char.isalnum() or char == '_':
        loc -= 1
      else:
        return None
    return None

  def on_query_completions(self, view, prefix, locations):
    if len(locations) > 1 or not view.file_name().endswith('.zig'):
      return None

    # cleanup before we start
    completions = []

    # dont bother with completions if we are in a comment block or string
    scope_name = view.scope_name(locations[0])
    no_completion_scopes = ['quoted.double', 'quoted.raw', 'comment.line', 'comment.block']
    if any(part in scope_name for part in no_completion_scopes):
      return None

    start_time = time.time()

    # extract the current text. If there is a '.' get the previous word to see if it matches a package
    file_view = sublime.active_window().find_open_file(view.file_name())
    curr_line_region = file_view.line(locations[0])
    curr_line = file_view.substr(curr_line_region).strip()

    # extract the string before the '.' in the current line if there is one and we are on the right side of it typing
    before_dot = self.get_prefix_before_dot(file_view, locations[0])

    # if we have no . in the text on the current line and it starts with '@' add the built-ins
    if before_dot == None:
      completions.extend(self.built_in_procs)

    #sort completions alphabetically
    if view.settings().get('zig_sort_completions_alphabetical', True):
      completions.sort()

    # Report time spent building completions before returning
    delta_time_ms = int((time.time() - start_time) * 1000)
    message = 'Zig autocompletion took ' + str(delta_time_ms) + 'ms. Completions: ' + str(len(completions))
    view.window().status_message(message)

    return completions


