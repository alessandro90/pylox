from __future__ import annotations  # NOTE: No need since python 3.11+
from typing import Iterator, Callable, Any, Type
from pyloxtoken import Token, TokenType
import expr as e
import stmt as s
from exceptions import InternalPyloxError, ParserError, ScannerError
from error_handler import report
from dataclasses import asdict


class Parser:
    _MAX_PARAMS = 255

    def __init__(self, tokens: Iterator[Token | None]):
        self._tokens = tokens
        self._current = self._try_get_next()
        self._has_error = False

    def parse(self) -> list[s.Stmt] | None:
        statements = []
        while not self._is_at_end():
            try:
                statement = self._declaration()
            except ParserError as e:
                report({"ParseError:": e})
            else:
                if not self._has_error and statement is not None:
                    statements.append(statement)
        if self._has_error:
            return None
        return statements

    def _declaration(self) -> s.Stmt | None:
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()
            if self._match(TokenType.FUN):
                self._current = self._expect(
                    TokenType.IDENTIFIER, "Expect function name"
                )  # Consume fun keyword
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParserError as e:
            report({"Parse error": e})
            self._synchronize()
            self._has_error = True
            return None

    def _class_declaration(self) -> s.Stmt:
        self._current = self._expect(TokenType.IDENTIFIER, "Expect class name.")
        name = self._current

        self._current = self._try_get_next()
        expect_brace = TokenType.LEFT_BRACE, "Expect '{' before class body."
        if (self._match(TokenType.LESS)):
            self._current = self._expect(
                TokenType.IDENTIFIER,
                "Expect superclass name."
            )
            superclass = e.Variable(self._current)
            self._current = self._expect(*expect_brace)
        else:
            superclass = None
            self._assert_token(self._current, *expect_brace)

        self._current = self._try_get_next()

        methods = []
        while not self._match(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))

        self._assert_token(
            self._current,
            TokenType.RIGHT_BRACE,
            "Expect '}' after class body."
        )
        self._current = self._try_get_next()
        return s.Class(name, superclass, methods)

    def _assert_max_arity(
        self,
        parameters: list[Token] | list[e.Expr],
        par_type: str
    ) -> None:
        if len(parameters) >= Parser._MAX_PARAMS:
            self._has_error = True
            report(
                asdict(self._current),
                f"Can't have more than {Parser._MAX_PARAMS} {par_type}."
            )

    def _function(self, fun: str) -> s.Stmt:
        name = self._current
        self._current = self._expect(
            TokenType.LEFT_PAREN, f"Expect '(' after {fun} name"
        )
        self._current = self._try_get_next()
        parameters: list[Token] = []
        if not self._match(TokenType.RIGHT_PAREN):
            self._assert_token(
                self._current,
                TokenType.IDENTIFIER,
                "Expect parameter name."
            )
            parameters = [self._current]
            self._current = self._try_get_next()
            while self._match(TokenType.COMMA):
                self._current = self._expect(
                    TokenType.IDENTIFIER, "Expect parameter name"
                )
                parameters.append(self._current)
                self._assert_max_arity(parameters, "paramters")
                self._current = self._try_get_next()

        self._assert_token(
            self._current,
            TokenType.RIGHT_PAREN,
            "Expect ')' after parameters."
        )

        self._current = self._expect(
            TokenType.LEFT_BRACE, f"Expect '{{' before {fun} body."
        )
        self._current = self._try_get_next()
        body = self._block()
        return s.Function(name, parameters, body)

    def _var_declaration(self) -> s.Stmt:
        self._current = self._try_get_next()
        name = self._current
        self._current = self._get_next_if_current_is(
            TokenType.IDENTIFIER, "Expect variable name."
        )

        initializer: e.Expr | None = None
        if self._match(TokenType.EQUAL):
            self._current = self._try_get_next()
            initializer = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after variable declaration"
        )
        return s.Var(name, initializer)

    def _statement(self) -> s.Stmt:
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            self._current = self._try_get_next()
            return self._if_statement()
        if self._match(TokenType.PRINT):
            self._current = self._try_get_next()
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            self._current = self._try_get_next()
            return s.Block(self._block())
        return self._expression_statement()

    def _return_statement(self) -> s.Stmt:
        keyword = self._current
        self._current = self._try_get_next()
        value: e.Expr | None = None
        if not self._match(TokenType.SEMICOLON):
            value = self._expression()

        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after return value."
        )
        return s.Return(keyword, value)

    def _for_statement(self) -> s.Stmt:
        self._current = self._try_get_next()

        self._current = self._get_next_if_current_is(
            TokenType.LEFT_PAREN, "Expect '(' after 'for'."
        )

        if self._match(TokenType.SEMICOLON):
            initializer = None
            self._current = self._try_get_next()
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: e.Expr | None = None
        if not self._match(TokenType.SEMICOLON):
            condition = self._expression()

        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after loop condition."
        )

        increment: e.Expr | None = None
        if not self._match(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_PAREN, "Expect ')' after for clauses."
        )

        body = self._statement()

        if increment is not None:
            body = s.Block([body, s.Expression(increment)])

        if condition is None:
            condition = e.Literal(True)

        body = s.While(condition, body)

        if initializer is not None:
            body = s.Block([initializer, body])

        return body

    def _while_statement(self) -> s.Stmt:
        self._current = self._try_get_next()
        self._current = self._get_next_if_current_is(
            TokenType.LEFT_PAREN, "Expect '(' after a 'while'."
        )
        condition = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_PAREN, "Expect ')' after condition."
        )
        body = self._statement()
        return s.While(condition, body)

    def _if_statement(self) -> s.Stmt:
        self._current = self._get_next_if_current_is(
            TokenType.LEFT_PAREN, "Expect '(' after if."
        )
        condition = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_PAREN, "Expect ')' after if body."
        )
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return s.If(condition, then_branch, else_branch)

    def _block(self) -> list[s.Stmt]:
        statements = []
        while not self._match(TokenType.RIGHT_BRACE) and not self._is_at_end():
            decl = self._declaration()
            if decl is not None:
                statements.append(decl)
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_BRACE, "Expect '}' after block."
        )
        return statements

    def _print_statement(self) -> s.Stmt:
        value = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after value."
        )
        return s.Print(value)

    def _expression_statement(self) -> s.Stmt:
        expression = self._expression()
        self._current = self._get_next_if_current_is(
            TokenType.SEMICOLON, "Expect ';' after expression."
        )
        return s.Expression(expression)

    def _try_get_next(self) -> Token:
        try:
            while (token := next(self._tokens)) is None:
                pass
            return token
        except ScannerError:
            self._has_error = True
            raise ParserError("Parse error due to previous scanner error.")
        except StopIteration:
            raise InternalPyloxError(
                f"Accessing non-existing token: {__file__}"
            )

    def _get_next_if_current_is(
        self, token_type: TokenType, message: str
    ) -> Token:
        if not self._match(token_type):
            self._has_error = True
            raise ParserError(self._current, message)
        return self._try_get_next()

    def _expect(self, token_type: TokenType, msg: str) -> Token:
        tkn = self._try_get_next()
        self._assert_token(tkn, token_type, msg)
        return tkn

    def _assert_token(
        self, token: Token, token_type: TokenType, msg: str
    ) -> None:
        if token.token_type is not token_type:
            self._has_error = True
            raise ParserError(token, msg)

    def _match(self, *token_types: TokenType) -> bool:
        return any(
            self._current.token_type == token_type for token_type in token_types
        )

    def _is_at_end(self) -> bool:
        return self._match(TokenType.EOF)

    def _expression(self) -> e.Expr:
        return self._assignment()

    def _assignment(self) -> e.Expr:
        expr = self._or()
        if self._match(TokenType.EQUAL):
            equals = self._current
            self._current = self._try_get_next()
            value = self._assignment()
            match expr:
                case e.Variable(name):
                    return e.Assign(name, value)  # noqa(F821)
                case e.Get(obj, name):
                    return e.Set(obj, name, value)  # noqa(F821)
                case _:
                    report(asdict(equals), "Invalid assignement target.")

        return expr

    def _or(self) -> e.Expr:
        return self._binary_expr(self._and, [TokenType.OR], e.Logical)

    def _and(self):
        return self._binary_expr(self._equality, [TokenType.AND], e.Logical)

    def _binary_expr(
        self,
        op: Callable[[], e.Expr],
        token_types: list[TokenType],
        expr_class: Type[e.Binary | e.Logical] = e.Binary,
    ) -> e.Expr:
        expression = op()
        while self._match(*token_types):
            operation = self._current
            self._current = self._try_get_next()
            right = op()
            expression = expr_class(expression, operation, right)
        return expression

    def _equality(self) -> e.Expr:
        return self._binary_expr(
            self._comparison, [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
        )

    def _comparison(self) -> e.Expr:
        return self._binary_expr(
            self._term,
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ],
            e.Binary,
        )

    def _term(self) -> e.Expr:
        return self._binary_expr(
            self._factor, [TokenType.MINUS, TokenType.PLUS]
        )

    def _factor(self) -> e.Expr:
        return self._binary_expr(self._unary, [TokenType.SLASH, TokenType.STAR])

    def _unary(self) -> e.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operation = self._current
            self._current = self._try_get_next()
            right = self._unary()
            return e.Unary(operation, right)
        return self._call()

    def _call(self) -> e.Expr:
        expr = self._primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                self._current = self._try_get_next()
                expr = self._finishCall(expr)
            elif self._match(TokenType.DOT):
                self._current = self._expect(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = e.Get(expr, self._current)
                self._current = self._try_get_next()
            else:
                break

        return expr

    def _finishCall(self, callee: e.Expr) -> e.Expr:
        arguments: list[e.Expr] = []
        if not self._match(TokenType.RIGHT_PAREN):
            while True:
                self._assert_max_arity(arguments, "arguments")
                arguments.append(self._expression())
                if self._match(TokenType.COMMA):
                    self._current = self._try_get_next()
                else:
                    break
        paren = self._current
        self._current = self._get_next_if_current_is(
            TokenType.RIGHT_PAREN, "Expect ')' after arguments."
        )
        return e.Call(callee, paren, arguments)

    def _find_literal(self, tokens: dict[TokenType, Any]) -> e.Expr | None:
        for token, literal in tokens.items():
            if self._match(token):
                ret = e.Literal(literal)
                self._current = self._try_get_next()
                return ret
        return None

    def _primary(self) -> e.Expr:
        if (
            literal := self._find_literal(
                {
                    TokenType.FALSE: False,
                    TokenType.TRUE: True,
                    TokenType.NIL: None,
                    TokenType.NUMBER: self._current.literal,
                    TokenType.STRING: self._current.literal,
                }
            )
        ) is not None:
            return literal

        if self._match(TokenType.SUPER):
            keyword = self._current
            self._current = self._expect(
                TokenType.DOT,
                "Expect '.' after super."
            )
            self._current = self._try_get_next()
            method, self._current = self._current, self._try_get_next()
            return e.Super(keyword, method)

        if self._match(TokenType.THIS):
            var, self._current = self._current, self._try_get_next()
            return e.This(var)

        if self._match(TokenType.IDENTIFIER):
            var = self._current
            self._current = self._try_get_next()
            return e.Variable(var)

        if self._match(TokenType.LEFT_PAREN):
            self._current = self._try_get_next()
            expression = self._expression()
            self._current = self._get_next_if_current_is(
                TokenType.RIGHT_PAREN, "Expect ')' after expression."
            )
            return e.Grouping(expression)

        self._has_error = True
        raise ParserError(
            f"Invalid primary expression:\n"
            f"Line: {self._current.line}\n"
            f"Expression: {self._current.lexeme}"
        )

    def _synchronize(self) -> None:
        while not self._is_at_end():
            if self._current.token_type == TokenType.SEMICOLON:
                self._current = self._try_get_next()
                return
            if any(
                token == self._current.token_type
                for token in (
                    TokenType.CLASS,
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.FOR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN,
                )
            ):
                return
            self._current = self._try_get_next()
